# Phase 1 Implementation: Multi-Stage Classification with Confidence Scoring

## Overview

Phase 1 implements a multi-stage classification pipeline that significantly improves routing accuracy by:

1. **Lower temperature LLM classification** (0.1) for more consistent results
2. **Confidence scoring** to measure classification reliability
3. **Semantic similarity matching** using weighted keywords
4. **Multi-stage fallback** system for handling ambiguous complaints

## What Changed

### 1. Configuration ([`src/config/settings.py`](src/config/settings.py))

Added new configuration options:

```python
classification_temperature: float = 0.1  # Lower for consistency
high_confidence_threshold: float = 0.8  # Threshold for high confidence
medium_confidence_threshold: float = 0.6  # Threshold for medium confidence
enable_semantic_matching: bool = True  # Enable/disable semantic matching
```

### 2. LLM Service ([`src/services/openrouter.py`](src/services/openrouter.py))

- Added separate `classification_llm` with lower temperature (0.1)
- Updated [`classify_complaint()`](src/services/openrouter.py:118) to return confidence scores
- Enhanced classification prompt to include confidence scoring guidelines

### 3. Semantic Matcher ([`src/services/semantic_matcher.py`](src/services/semantic_matcher.py)) - NEW

Created a new semantic matching system that:

- Uses weighted keywords (high, medium, low weights)
- Calculates similarity scores based on keyword matches
- Returns matched keywords for transparency
- Supports synonym matching (e.g., "vehicles" ≈ "cars")

### 4. Router ([`src/services/router.py`](src/services/router.py))

Updated [`ComplaintRouter`](src/services/router.py:14) class:

- Added [`SemanticMatcher`](src/services/semantic_matcher.py:49) integration
- Implemented [`_multi_stage_classify()`](src/services/router.py:48) method with 4 stages:
  - **Stage 1**: LLM classification (confidence ≥ 0.8)
  - **Stage 2**: Semantic matching (similarity ≥ 0.8)
  - **Stage 3**: Hybrid approach (similarity ≥ 0.6)
  - **Stage 4**: LLM fallback

### 5. Environment Configuration ([`.env.example`](.env.example))

Added new environment variables:

```bash
CLASSIFICATION_TEMPERATURE=0.1
HIGH_CONFIDENCE_THRESHOLD=0.8
MEDIUM_CONFIDENCE_THRESHOLD=0.6
ENABLE_SEMANTIC_MATCHING=true
```

### 6. Dependencies ([`pyproject.toml`](pyproject.toml))

Added required packages:

```toml
numpy>=1.24.0
scikit-learn>=1.3.0
```

## How It Works

### Multi-Stage Classification Pipeline

```
Complaint Input
    ↓
Stage 1: LLM Classification (temp: 0.1)
    ↓
Confidence ≥ 0.8?
    ├─ Yes → Use LLM classification
    └─ No → Stage 2
        ↓
Stage 2: Semantic Similarity Match
    ↓
Similarity ≥ 0.8?
    ├─ Yes → Use semantic match
    └─ No → Stage 3
        ↓
Stage 3: Hybrid Approach
    ↓
Similarity ≥ 0.6?
    ├─ Yes → Use semantic category + LLM severity/urgency
    └─ No → Stage 4
        ↓
Stage 4: LLM Fallback
    ↓
Use LLM classification regardless of confidence
```

### Example Workflow

**Input**: "Too many cars at UiTM Shah Alam"

**Stage 1 (LLM)**:

```json
{
  "category": "traffic",
  "severity": "medium",
  "urgency": "routine",
  "keywords": ["cars", "traffic"],
  "summary": "Too many cars at UiTM Shah Alam",
  "confidence": 0.85
}
```

Since confidence (0.85) ≥ high threshold (0.8), use LLM classification.

**Result**:

- Category: traffic
- Method: llm
- Confidence: 0.85
- Department: Traffic Management Department

### Example with Low Confidence

**Input**: "There's an issue somewhere"

**Stage 1 (LLM)**:

```json
{
  "category": "general",
  "severity": "medium",
  "urgency": "routine",
  "keywords": [],
  "summary": "There's an issue somewhere",
  "confidence": 0.3
}
```

Since confidence (0.3) < high threshold (0.8), proceed to Stage 2.

**Stage 2 (Semantic)**:

```json
{
  "category": "general",
  "similarity": 0.1,
  "matched_keywords": []
}
```

Since similarity (0.1) < high threshold (0.8), proceed to Stage 3.

**Stage 3 (Hybrid)**:

```json
{
  "category": "general",
  "similarity": 0.1
}
```

Since similarity (0.1) < medium threshold (0.6), proceed to Stage 4.

**Stage 4 (Fallback)**:
Use LLM classification from Stage 1.

## Benefits

### Before Phase 1

- ❌ Rigid keyword matching (exact substring only)
- ❌ No semantic understanding ("vehicles" ≠ "cars")
- ❌ High temperature (0.7) → inconsistent classifications
- ❌ No confidence scoring
- ❌ Single-shot classification

### After Phase 1

- ✅ Weighted keyword matching with synonyms
- ✅ Semantic understanding through keyword weights
- ✅ Low temperature (0.1) → consistent classifications
- ✅ Confidence scoring for reliability measurement
- ✅ Multi-stage fallback system
- ✅ Transparent classification method tracking

## Usage

### Basic Usage

```python
from src.services.router import ComplaintRouter

router = ComplaintRouter()

result = router.route_complaint(
    complaint="Too many cars at UiTM Shah Alam"
)

print(f"Category: {result['classification']['category']}")
print(f"Method: {result['classification'].get('classification_method')}")
print(f"Confidence: {result['classification'].get('classification_confidence')}")
print(f"Department: {result['department']['name']}")
```

### With Location Data

```python
result = router.route_complaint(
    complaint="Broken street light at Central Market",
    location_data={
        "lat": 3.1517,
        "lng": 101.6945,
        "place_name": "Central Market"
    }
)
```

### With User Info

```python
result = router.route_complaint(
    complaint="Trash everywhere in the park",
    user_info={
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+60-12-345-6789"
    }
)
```

## Testing

Run the Phase 1 tests:

```bash
python tests/test_phase1_routing.py
```

The test suite includes:

1. **Semantic Matcher Tests**: Verifies keyword matching and similarity scoring
2. **Multi-Stage Classification Tests**: Tests the full pipeline (requires API keys)
3. **Confidence Scoring Tests**: Validates confidence scoring (requires API keys)
4. **Keyword Matching Tests**: Tests synonym and related term matching

## Configuration

Adjust the following in your `.env` file:

```bash
# Lower temperature for more consistent classifications
CLASSIFICATION_TEMPERATURE=0.1

# Confidence thresholds
HIGH_CONFIDENCE_THRESHOLD=0.8
MEDIUM_CONFIDENCE_THRESHOLD=0.6

# Enable/disable semantic matching
ENABLE_SEMANTIC_MATCHING=true
```

## Next Steps (Phase 2)

Phase 2 will implement:

1. **Multi-label classification**: Route to multiple departments when appropriate
2. **Context-aware routing**: Apply rules based on location, time, and weather
3. **Priority calculation**: Enhanced priority scoring with context factors

## Troubleshooting

### Low Confidence Scores

If you're seeing low confidence scores:

1. Check the complaint text - is it clear and specific?
2. Review the classification prompt in [`openrouter.py`](src/services/openrouter.py:136)
3. Adjust confidence thresholds in `.env`

### Semantic Matching Not Working

If semantic matching is not being used:

1. Check `ENABLE_SEMANTIC_MATCHING=true` in `.env`
2. Verify the semantic matcher is initialized in [`router.py`](src/services/router.py:29)
3. Check the keyword weights in [`semantic_matcher.py`](src/services/semantic_matcher.py:69)

### Inconsistent Classifications

If classifications are still inconsistent:

1. Verify `CLASSIFICATION_TEMPERATURE=0.1` in `.env`
2. Check that the classification LLM is using the correct temperature
3. Review the classification prompt for clarity

## Files Modified

- [`src/config/settings.py`](src/config/settings.py) - Added new configuration options
- [`src/services/openrouter.py`](src/services/openrouter.py) - Added confidence scoring
- [`src/services/router.py`](src/services/router.py) - Implemented multi-stage pipeline
- [`.env.example`](.env.example) - Added new environment variables
- [`pyproject.toml`](pyproject.toml) - Added dependencies

## Files Created

- [`src/services/semantic_matcher.py`](src/services/semantic_matcher.py) - New semantic matching service
- [`tests/test_phase1_routing.py`](tests/test_phase1_routing.py) - Phase 1 test suite
- `PHASE1_IMPLEMENTATION.md` - This documentation

## Summary

Phase 1 successfully implements a multi-stage classification pipeline that:

- ✅ Uses lower temperature (0.1) for consistent LLM classifications
- ✅ Adds confidence scoring to measure reliability
- ✅ Implements semantic similarity matching with weighted keywords
- ✅ Provides multi-stage fallback for ambiguous complaints
- ✅ Maintains backward compatibility with existing code

The system is now more intelligent and accurate, with better handling of:

- Synonyms and related terms
- Ambiguous complaints
- Low-confidence classifications
- Edge cases

Ready for Phase 2 implementation upon approval.
