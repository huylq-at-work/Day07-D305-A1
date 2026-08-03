#!/usr/bin/env python3
"""
Benchmark script for Phase 6 - Strategy comparison

Usage:
    python bench.py --strategy fixed --chunk-size 500 --overlap 50
    python bench.py --strategy sentence --max-sentences 3
    python bench.py --strategy recursive --chunk-size 400
"""

import argparse
import yaml
from pathlib import Path

from ingest import build_knowledge_base
from src import (
    FixedSizeChunker,
    SentenceChunker, 
    RecursiveChunker,
    LocalEmbedder,
    MockEmbedder,
    KnowledgeBaseAgent,
    _mock_embed
)


def parse_args():
    parser = argparse.ArgumentParser(description='Run benchmark with different chunking strategies')
    parser.add_argument('--strategy', choices=['fixed', 'sentence', 'recursive'], 
                       default='fixed', help='Chunking strategy to use')
    parser.add_argument('--chunk-size', type=int, default=500,
                       help='Chunk size for fixed/recursive (default: 500)')
    parser.add_argument('--overlap', type=int, default=50,
                       help='Overlap for fixed chunker (default: 50)')
    parser.add_argument('--max-sentences', type=int, default=3,
                       help='Max sentences per chunk for sentence chunker (default: 3)')
    parser.add_argument('--corpus', default='data/k3_university',
                       help='Corpus directory (default: data/k3_university)')
    parser.add_argument('--queries', default='data/benchmark_queries.yaml',
                       help='Queries file (default: data/benchmark_queries.yaml)')
    parser.add_argument('--embedder', choices=['mock', 'local'], default='local',
                       help='Embedder to use (default: local)')
    parser.add_argument('--top-k', type=int, default=3,
                       help='Number of top results to show (default: 3)')
    return parser.parse_args()


def get_chunker(args):
    """Select chunker based on strategy."""
    if args.strategy == 'fixed':
        return FixedSizeChunker(chunk_size=args.chunk_size, overlap=args.overlap)
    elif args.strategy == 'sentence':
        return SentenceChunker(max_sentences_per_chunk=args.max_sentences)
    elif args.strategy == 'recursive':
        return RecursiveChunker(chunk_size=args.chunk_size)
    else:
        raise ValueError(f"Unknown strategy: {args.strategy}")


def get_embedder(embedder_type):
    """Get embedding function."""
    if embedder_type == 'mock':
        print("⚠️  WARNING: Using mock embedder - results won't reflect semantic quality!")
        return _mock_embed
    else:
        try:
            embedder = LocalEmbedder()
            print(f"✓ Using embedder: {embedder._backend_name}")
            return embedder
        except Exception as e:
            print(f"⚠️  Failed to load local embedder: {e}")
            print("⚠️  Falling back to mock embedder")
            return _mock_embed


def format_params(args):
    """Format parameters for display."""
    if args.strategy == 'fixed':
        return f"chunk_size={args.chunk_size}, overlap={args.overlap}"
    elif args.strategy == 'sentence':
        return f"max_sentences={args.max_sentences}"
    elif args.strategy == 'recursive':
        return f"chunk_size={args.chunk_size}"
    return ""


def main():
    args = parse_args()
    
    print("=" * 80)
    print("📊 BENCHMARK - Phase 6: Strategy & Retrieval Quality")
    print("=" * 80)
    
    # 1. Select chunker (ONLY LINE that differs between team members)
    chunker = get_chunker(args)
    print(f"\n🔧 Strategy: {args.strategy}")
    print(f"   Parameters: {format_params(args)}")
    
    # 2. Get embedder
    embedding_fn = get_embedder(args.embedder)
    
    # 3. Build knowledge base (ingest.py does everything)
    print(f"\n📚 Loading corpus from: {args.corpus}")
    store = build_knowledge_base(args.corpus, embedding_fn, chunker=chunker)
    n_chunks = store.get_collection_size()
    print(f"✓ Loaded {n_chunks} chunks")
    
    # 4. Load queries
    print(f"\n📋 Loading queries from: {args.queries}")
    with open(args.queries, 'r', encoding='utf-8') as f:
        queries_data = yaml.safe_load(f)
    queries = queries_data['queries']
    print(f"✓ Loaded {len(queries)} queries")
    
    # 5. Create agent
    def mock_llm(prompt):
        return "Answer based on context."
    
    agent = KnowledgeBaseAgent(store=store, llm_fn=mock_llm)
    
    # 6. Run benchmark
    print("\n" + "=" * 80)
    print("🎯 RUNNING BENCHMARK")
    print("=" * 80)
    
    for i, q in enumerate(queries, 1):
        print(f"\n{'─' * 80}")
        print(f"Query {i}/5: {q['id']} ({q['kind']})")
        print(f"{'─' * 80}")
        print(f"❓ {q['question']}")
        
        # Search with or without filter
        metadata_filter = q.get('metadata_filter')
        if metadata_filter:
            print(f"🔍 Filter: {metadata_filter}")
            results = store.search_with_filter(
                q['question'], 
                top_k=args.top_k,
                metadata_filter=metadata_filter
            )
        else:
            results = store.search(q['question'], top_k=args.top_k)
        
        print(f"\n📊 Top-{args.top_k} Results:")
        for j, r in enumerate(results, 1):
            doc_id = r.get('metadata', {}).get('doc_id', 'unknown')
            score = r.get('score', 0.0)
            content = r.get('content', '')[:100].replace('\n', ' ')
            
            # Check if this is the gold document
            is_gold = (doc_id == q['gold_doc_id'])
            marker = "✓✓✓" if is_gold else "   "
            
            print(f"{marker} [{j}] Score: {score:.4f} | Doc: {doc_id}")
            print(f"        Preview: {content}...")
        
        # Get agent answer
        answer = agent.answer(q['question'], top_k=args.top_k)
        print(f"\n🤖 Agent Answer: {answer[:200]}...")
        
        # Show gold answer for comparison
        print(f"\n✅ Gold Answer: {q['gold_answer'][:200]}...")
    
    # 7. Summary
    print("\n" + "=" * 80)
    print("📈 SUMMARY")
    print("=" * 80)
    print(f"Strategy: {args.strategy} ({format_params(args)})")
    print(f"Total chunks: {n_chunks}")
    print(f"Queries run: {len(queries)}")
    print(f"Top-k: {args.top_k}")
    print("\n✓ Benchmark complete!")
    print("\n💡 Next steps:")
    print("   1. Compare results with other team members")
    print("   2. Identify which queries succeeded/failed")
    print("   3. Analyze failure cases")
    print("   4. Fill in REPORT_CANHAN.md Section 5")
    print("   5. Contribute to REPORT_NHOM.md analysis")


if __name__ == '__main__':
    main()
