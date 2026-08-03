#!/usr/bin/env python3
"""
Benchmark script that saves results to CSV

Usage:
    python bench_to_csv.py --strategy fixed --chunk-size 500 --overlap 50
    python bench_to_csv.py --strategy recursive --chunk-size 400
"""

import argparse
import yaml
import csv
from datetime import datetime
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
    parser.add_argument('--top-k', type=int, default=5,
                       help='Number of top results to retrieve (default: 5)')
    parser.add_argument('--output', default='results/benchmark_results.csv',
                       help='Output CSV file (default: results/benchmark_results.csv)')
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
    print("📊 BENCHMARK - Saving Results to CSV")
    print("=" * 80)
    
    # 1. Select chunker
    chunker = get_chunker(args)
    print(f"\n🔧 Strategy: {args.strategy}")
    print(f"   Parameters: {format_params(args)}")
    
    # 2. Get embedder
    embedding_fn = get_embedder(args.embedder)
    
    # 3. Build knowledge base
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
    
    # 6. Prepare output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 7. Run benchmark and collect results
    print("\n" + "=" * 80)
    print("🎯 RUNNING BENCHMARK")
    print("=" * 80)
    
    all_results = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
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
        
        # Find gold rank
        gold_rank = None
        for rank, r in enumerate(results, 1):
            doc_id = r.get('metadata', {}).get('doc_id', 'unknown')
            if doc_id == q['gold_doc_id']:
                gold_rank = rank
                break
        
        # Calculate rubric score
        if gold_rank == 1:
            rubric_score = 2
        elif gold_rank and gold_rank <= 3:
            rubric_score = 1
        else:
            rubric_score = 0
        
        print(f"\n📊 Top-{min(args.top_k, len(results))} Results:")
        for j, r in enumerate(results[:args.top_k], 1):
            doc_id = r.get('metadata', {}).get('doc_id', 'unknown')
            score = r.get('score', 0.0)
            content = r.get('content', '')[:80].replace('\n', ' ')
            
            is_gold = (doc_id == q['gold_doc_id'])
            marker = "✓✓✓" if is_gold else "   "
            
            print(f"{marker} [{j}] Score: {score:.4f} | Doc: {doc_id}")
            print(f"        Preview: {content}...")
            
            # Save to results (one row per retrieved chunk)
            all_results.append({
                'timestamp': timestamp,
                'strategy': args.strategy,
                'params': format_params(args),
                'total_chunks': n_chunks,
                'embedder': args.embedder,
                'query_id': q['id'],
                'query_kind': q['kind'],
                'query_text': q['question'],
                'has_filter': 'yes' if metadata_filter else 'no',
                'filter': str(metadata_filter) if metadata_filter else '',
                'gold_doc_id': q['gold_doc_id'],
                'gold_rank': gold_rank if gold_rank else 'N/A',
                'rubric_score': rubric_score,
                'rank': j,
                'retrieved_doc_id': doc_id,
                'similarity_score': score,
                'is_gold': 'yes' if is_gold else 'no',
                'content_preview': r.get('content', '')[:200].replace('\n', ' ')
            })
        
        print(f"\n🎯 Gold doc: {q['gold_doc_id']}")
        print(f"   Gold rank: {gold_rank if gold_rank else 'NOT FOUND'}")
        print(f"   Rubric score: {rubric_score}/2")
    
    # 8. Save to CSV
    print("\n" + "=" * 80)
    print("💾 SAVING RESULTS TO CSV")
    print("=" * 80)
    
    fieldnames = [
        'timestamp', 'strategy', 'params', 'total_chunks', 'embedder',
        'query_id', 'query_kind', 'query_text', 'has_filter', 'filter',
        'gold_doc_id', 'gold_rank', 'rubric_score',
        'rank', 'retrieved_doc_id', 'similarity_score', 'is_gold', 'content_preview'
    ]
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)
    
    print(f"✓ Saved {len(all_results)} rows to {output_path}")
    
    # 9. Summary
    total_score = sum(r['rubric_score'] for r in all_results if r['rank'] == 1)
    successful_queries = sum(1 for r in all_results if r['rank'] == 1 and r['rubric_score'] == 2)
    
    print("\n" + "=" * 80)
    print("📈 SUMMARY")
    print("=" * 80)
    print(f"Strategy: {args.strategy} ({format_params(args)})")
    print(f"Total chunks: {n_chunks}")
    print(f"Queries run: {len(queries)}")
    print(f"Total score: {total_score}/10 ({total_score/10*100:.0f}%)")
    print(f"Successful queries: {successful_queries}/{len(queries)}")
    print(f"\n✓ Results saved to: {output_path}")
    print(f"\n💡 Next steps:")
    print(f"   1. Open {output_path} in Excel/spreadsheet")
    print(f"   2. Analyze gold_rank and rubric_score columns")
    print(f"   3. Compare with other strategies")


if __name__ == '__main__':
    main()
