# Merge Strategy: Integrating Traceability into Main Branch

**Last Updated**: 2025-11-15
**Purpose**: Guide for safely merging supply chain traceability work into main branch
**Source Branch**: `feature/pr15-aggregation`
**Target Branch**: `main`

---

## Overview

The `feature/pr15-aggregation` branch contains completed supply chain traceability work (PR13-PR15):
- **PR13**: Supplier, MaterialLot, Order, ProductionBatch models + data generation
- **PR14**: Batch tracking with material linkage and order assignment
- **PR15**: Aggregation function (batches → production structure for backward compatibility)

**Challenge**: Feature branch has DELETED deployment infrastructure that exists on main:
- Removed `.github/workflows/` (CI/CD pipelines)
- Removed `infra/` (Bicep templates)
- Removed `backend/Dockerfile`
- Heavily trimmed `implementation-plan.md` (-3112 lines)

**Goal**: Cherry-pick traceability commits while preserving main's deployment infrastructure.

---

## Strategy: Selective Cherry-Pick

### Step 1: Identify Commits to Cherry-Pick

```bash
# View feature branch commits
git log --oneline feature/pr15-aggregation --not main

# Expected commits (example):
# abc1234 feat: Add aggregation function (PR15)
# def5678 feat: Add ProductionBatch model (PR14)
# ghi9012 feat: Add supply chain models (PR13)
```

### Step 2: Create Integration Branch

```bash
# Start from clean main branch
git checkout main
git pull origin main

# Create new integration branch
git checkout -b feature/integrated-traceability
```

### Step 3: Cherry-Pick Traceability Commits

**Files to Cherry-Pick**:
- `shared/models.py` - New Pydantic models
- `shared/data_generator.py` - Generation functions
- `shared/data.py` - Aggregation function
- `tests/test_*.py` - New test files
- `docs/traceability_examples.py` - Documentation
- `docs/PR14_SUMMARY.md` - Documentation
- `PR13_SUMMARY.md` - Documentation

**Files to SKIP** (keep main's versions):
- `.github/workflows/` - Keep main's CI/CD
- `infra/` - Keep main's Bicep templates
- `backend/Dockerfile` - Keep main's Docker config
- `implementation-plan.md` - Will create new plan (Nov15-plan.md)

**Cherry-Pick Command**:
```bash
# Cherry-pick specific commits (replace with actual commit SHAs)
git cherry-pick abc1234  # PR13: Supply chain models
git cherry-pick def5678  # PR14: ProductionBatch model
git cherry-pick ghi9012  # PR15: Aggregation function

# If conflicts occur on files we want to skip:
git checkout --ours .github/workflows/
git checkout --ours infra/
git checkout --ours backend/Dockerfile
git add .github/ infra/ backend/Dockerfile
git cherry-pick --continue
```

---

## Alternative Strategy: Manual Merge (If Cherry-Pick Fails)

If cherry-pick becomes too complex due to conflicts, use manual merge:

### Step 1: Read Feature Branch Files

```bash
# Show file contents from feature branch
git show feature/pr15-aggregation:shared/models.py > /tmp/models_new.py
git show feature/pr15-aggregation:shared/data_generator.py > /tmp/data_gen_new.py
git show feature/pr15-aggregation:shared/data.py > /tmp/data_new.py
```

### Step 2: Manually Copy Changes

1. **Models** (`shared/models.py`):
   - Add: Supplier, MaterialSpec, MaterialLot, Order, ProductionBatch, MaterialUsage classes
   - Keep: Existing models (OEEMetrics, ScrapMetrics, etc.)

2. **Data Generator** (`shared/data_generator.py`):
   - Add: generate_suppliers(), generate_materials_catalog(), generate_material_lots()
   - Add: generate_orders(), generate_production_batches()
   - Update: generate_production_data() to call new functions

3. **Data Module** (`shared/data.py`):
   - Add: aggregate_batches_to_production() function
   - Keep: Existing load_data_async(), save_data_async() functions

4. **Tests**:
   - Copy new test files: test_supply_chain_models.py, test_aggregation.py
   - Update existing tests if needed

### Step 3: Verify Integration

```bash
# Run all tests
pytest tests/ -v

# Verify data generation
python -m src.main setup

# Check generated data structure
cat data/production.json | jq 'keys'
# Expected: ["suppliers", "materials_catalog", "material_lots", "orders", "production_batches", "production", ...]
```

---

## Conflict Resolution Guide

### Common Conflicts and Solutions

**1. `shared/models.py` conflict**:
```bash
# Keep both versions - main's existing models + feature's new models
git checkout --merge shared/models.py
# Manually edit to include ALL models
```

**2. `shared/data_generator.py` conflict**:
```bash
# Feature branch has new functions, main may have updates to existing functions
git checkout --merge shared/data_generator.py
# Manually merge: Keep main's bug fixes + add feature's new functions
```

**3. `.github/workflows/` conflict**:
```bash
# Always keep main's version (has working CI/CD)
git checkout --ours .github/
```

**4. `implementation-plan.md` conflict**:
```bash
# Skip both - we're creating Nov15-plan.md instead
git rm implementation-plan.md
# Will create new plan later
```

---

## Validation Checklist

After merging, verify:

- [ ] All tests pass: `pytest tests/ -v`
- [ ] Data generation works: `python -m src.main setup`
- [ ] Generated data has new fields:
  ```bash
  cat data/production.json | jq 'keys'
  # Should include: suppliers, materials_catalog, material_lots, orders, production_batches
  ```
- [ ] Existing functionality unchanged:
  - Backend API still works: `uvicorn backend.src.api.main:app --reload`
  - `/api/metrics/oee` endpoint works
  - `/api/chat` endpoint works
- [ ] Deployment infrastructure intact:
  - `.github/workflows/deploy-backend.yml` exists
  - `infra/main.bicep` exists
  - `backend/Dockerfile` exists
- [ ] New models importable:
  ```python
  from shared.models import Supplier, MaterialLot, Order, ProductionBatch
  ```
- [ ] Aggregation function works:
  ```python
  from shared.data import aggregate_batches_to_production
  # Should run without errors
  ```

---

## Post-Merge Actions

After successful merge:

1. **Update documentation**:
   - Create Nov15-plan.md (new integrated plan)
   - Update README.md (mention traceability features)
   - Keep ARCHIVE-completed-prs.md for reference

2. **Delete feature branch** (optional):
   ```bash
   git branch -d feature/pr15-aggregation
   git push origin --delete feature/pr15-aggregation
   ```

3. **Create PR for Phase 2**:
   - Next PR: Add traceability API endpoints
   - Build on merged foundation

---

## Troubleshooting

### Issue: Cherry-pick fails with merge conflicts

**Solution**: Use manual merge strategy (see Alternative Strategy section)

### Issue: Tests fail after merge

**Solution**:
1. Check for missing imports
2. Verify all new model files are present
3. Run `pip install -r backend/requirements.txt` (in case dependencies changed)
4. Check test files for path issues

### Issue: Data generation creates incorrect structure

**Solution**:
1. Verify `generate_production_data()` calls all new generation functions
2. Check aggregation function is called
3. Look for errors in `data.py` aggregation logic

### Issue: Deployment infrastructure missing

**Solution**:
1. Ensure you kept main's `.github/`, `infra/`, `backend/Dockerfile`
2. If accidentally deleted: `git checkout main -- .github/ infra/ backend/Dockerfile`

---

## Summary

**Recommended Approach**: Cherry-pick commits, skip deployment files

**Key Principle**: Add traceability models/data WITHOUT breaking existing deployment

**Success Criteria**:
- All traceability models available
- Data generation includes batches + aggregation
- Tests pass
- Deployment infrastructure unchanged
- Backward compatibility maintained (existing metrics still work)

**Next Step After Merge**: Implement Phase 2 (Traceability API endpoints)
