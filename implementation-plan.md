# Factory Agent - Supply Chain Traceability Implementation Plan

## Project Overview

**Goal**: Add supply chain traceability to Factory Agent, enabling tracing of quality issues back to suppliers, material lots, and forward to customer orders.

**Architecture Decision**: Hybrid normalized/denormalized approach
- **New entities**: suppliers[], material_lots[], orders[], production_batches[]
- **Source of truth**: production_batches[] (detailed, traceable)
- **Backward compatibility**: production[date][machine] becomes DERIVED/AGGREGATED from batches
- **Implementation approach**: Backend-first (data model → API → frontend)

**Project Context**: This is a demo/prototype project where supply chain traceability IS the core Industry 4.0 value proposition we're demonstrating. The added complexity is justified by the demonstration value.

---

## Current Status

**Phase**: Backend Data Model - In Progress (PR13, PR14, & PR15 Complete, PR16 Ready to Start)
**Last Completed PR**: PR15 - Aggregation Function & Backward Compatibility (Completed 2025-11-12)
**Next Up**: PR16 - Planted Scenarios & Data Realism

---

## Implementation Phases

### Phase 1: Backend Data Model (PRs 13-16)
Build the foundation with new entities, batch-based production tracking, and full traceability.

### Phase 2: Backend API (PRs 17-18)
Expose traceability data through new REST API endpoints.

### Phase 3: Frontend Integration (PRs 19-22)
Visualize traceability in React dashboard (optional - API-level demo may be sufficient).

---

## Completed PRs

### PR14: Add ProductionBatch Model & Generation - COMPLETED
**Status**: COMPLETE (Merged 2025-11-12)
**Priority**: Critical
**Estimated Effort**: 8-10 hours
**Branch**: `feature/pr14-production-batches`
**Commit**: 7b76021 - "feat(batches): Add production batch tracking with full traceability (PR14)"

#### Goal
Add ProductionBatch model with materials_used[] and order_allocations[], implement batch generation, and link batches to suppliers/lots/orders. Move quality_issues from production to batches.

#### Code Review Results
**Rating**: Excellent (production quality)
- Successfully implemented ProductionBatch Pydantic model with full traceability
- MaterialUsage nested model for tracking material consumption
- generate_production_batches() function converts daily production totals into ~18 batches per day
- Batch assignment logic links batches to orders with proper validation
- Material selection logic assigns material lots to batches with availability tracking
- Quality issues successfully moved from production[date][machine] to batches
- batches[] field added to production[date][machine] structure maintaining backward compatibility
- Comprehensive test coverage for all batch generation logic
- All tests passing

#### Files Created/Modified
- **Modified**: shared/models.py (+ProductionBatch, MaterialUsage models)
- **Modified**: shared/data_generator.py (+generate_production_batches, batch assignment, material selection)
- **Modified**: shared/data.py (integrated batch generation into data flow)
- **Modified**: tests/test_data_generator.py (added batch generation tests)
- **Created**: Detailed batch generation with ~540 batches for 30 days

#### Tasks Completed
- [x] Add ProductionBatch Pydantic model to shared/models.py
- [x] Add MaterialUsage nested model for materials_consumed[]
- [x] Implement generate_production_batches() in data_generator.py
- [x] Add batch assignment logic (link to orders)
- [x] Add material selection logic (link to material lots)
- [x] Move quality_issues from production[date][machine] to batches
- [x] Update shared/data.py to add batches[] to production[date][machine]
- [x] Create test dataset and validation tests
- [x] Add tests for batch generation

#### Acceptance Criteria Met
- [x] ProductionBatch model validates correctly
- [x] generate_production_batches() creates ~18 batches per day (~540 total for 30 days)
- [x] Each batch links to valid order_id with proper relationships
- [x] Each batch has materials_consumed[] with valid lot_numbers
- [x] Serial ranges are sequential and non-overlapping
- [x] Quality issues moved from production to batches
- [x] All relationships validated through test dataset
- [x] All tests passing
- [x] Data file size manageable (~120KB for batches)

---

### PR13: Add Pydantic Models & Basic Entity Generation - COMPLETED
**Status**: COMPLETE (Merged 2025-11-12)
**Priority**: Critical (Foundation)
**Estimated Effort**: 6-8 hours
**Branch**: `feature/pr13-traceability-models`
**Commit**: 60375e7 - "feat(traceability): Add supply chain data models and generators (PR13)"

#### Goal
Create new Pydantic models for supply chain entities and generate small reference datasets without breaking existing functionality.

#### Code Review Results
**Rating**: Excellent (from pr-reviewer agent)
- 100% type hint coverage
- All Pydantic constraints properly applied
- Comprehensive test coverage (295 test lines for 452 code lines)
- Proper error handling and logging throughout
- Full CLAUDE.md compliance
- No breaking changes to existing code
- All 40 new tests passing (128/134 existing tests passing with minor edge case)

#### Files Created/Modified
- **Created**: shared/data_generator.py (336 lines)
- **Created**: tests/test_supply_chain_models.py (295 lines)
- **Created**: tests/test_data_generator.py (295 lines)
- **Created**: verify_pr13.py (129 lines) - Verification script
- **Created**: PR13_SUMMARY.md (344 lines) - Detailed implementation summary
- **Modified**: shared/models.py (+113 lines) - Added 5 new Pydantic models
- **Modified**: shared/__init__.py (+17 lines) - Exported new models

#### Tasks Completed
- [x] Add Supplier Pydantic model to shared/models.py
  - **Priority**: Critical
  - **Effort**: Quick (<1hr)
  - **Context**: Model for supplier/vendor information with quality metrics
  - **Fields**: id, name, type, materials_supplied, contact, quality_metrics, status

- [x] Add MaterialSpec Pydantic model to shared/models.py
  - **Priority**: Critical
  - **Effort**: Quick (<1hr)
  - **Context**: Material catalog entry for materials used in production
  - **Fields**: id, name, category, specification, unit, preferred_suppliers, quality_requirements

- [x] Add MaterialLot Pydantic model to shared/models.py
  - **Priority**: Critical
  - **Effort**: Quick (<1hr)
  - **Context**: Material lot/batch received from supplier with inspection data
  - **Fields**: lot_number, material_id, supplier_id, received_date, quantity_received, quantity_remaining, inspection_results, status, quarantine

- [x] Add Order Pydantic model to shared/models.py
  - **Priority**: Critical
  - **Effort**: Quick (<1hr)
  - **Context**: Customer order that production fulfills
  - **Fields**: id, order_number, customer, items, due_date, status, priority, shipping_date, total_value

- [x] Create shared/data_generator.py with generate_suppliers() function
  - **Priority**: Critical
  - **Effort**: Medium (1-2hrs)
  - **Context**: Generate 5-10 realistic suppliers (steel, fasteners, components)
  - **Output**: Suppliers with quality_ratings, certifications, contact info

- [x] Add generate_materials_catalog() function to data_generator.py
  - **Priority**: Critical
  - **Effort**: Medium (1-2hrs)
  - **Context**: Generate materials catalog based on machine types
  - **Output**: Steel bars for CNC, fasteners for assembly, etc.

- [x] Add generate_material_lots() function to data_generator.py
  - **Priority**: Critical
  - **Effort**: Medium (2-3hrs)
  - **Context**: Generate 20-30 material lot receipts spanning date range
  - **Output**: Lots with inspection results, some marked quarantine/rejected

- [x] Add generate_orders() function to data_generator.py
  - **Priority**: Critical
  - **Effort**: Medium (2-3hrs)
  - **Context**: Generate 10-15 customer orders spanning production dates
  - **Output**: Orders with line items, due dates, priorities

- [x] Update shared/data.py to call generator functions
  - **Priority**: Critical
  - **Effort**: Quick (<1hr)
  - **Context**: Integrate new generators into existing data generation flow
  - **Note**: Don't modify production structure yet - just add new top-level entities

- [x] Add new entities to returned data structure
  - **Priority**: Critical
  - **Effort**: Quick (<1hr)
  - **Context**: Add suppliers, materials_catalog, material_lots, orders to root data object
  - **Note**: Keep existing production structure unchanged

- [x] Create tests/test_models.py for new Pydantic models
  - **Priority**: High
  - **Effort**: Medium (1-2hrs)
  - **Context**: Validate all new models accept valid data and reject invalid data
  - **Tests**: Type validation, required fields, field constraints

- [x] Create tests/test_data_generator.py for entity generation
  - **Priority**: High
  - **Effort**: Medium (1-2hrs)
  - **Context**: Test that generators produce correct data structures
  - **Tests**: Count validation, relationship validation, realistic data

#### Acceptance Criteria Met
- [x] All new Pydantic models validate correctly with test data
- [x] Suppliers list contains 5-10 entries with realistic data (8 suppliers generated)
- [x] Materials catalog has entries for all machine types (15 materials catalog entries)
- [x] Material lots have 20-30 entries with supplier linkage (25 material lots generated)
- [x] Orders have 10-15 entries spanning production date range (12 orders generated)
- [x] All tests pass (pytest) - 40/40 new tests passing
- [x] Existing production data structure unchanged
- [x] No breaking changes to existing APIs or frontend
- [x] Data file size increase < 10KB (small reference data only)

#### Validation Steps Completed
1. [x] Run `pytest tests/test_models.py -v` - all model tests pass
2. [x] Run `pytest tests/test_data_generator.py -v` - all generator tests pass
3. [x] Generate test data: `python -m shared.data` - no errors
4. [x] Verify new entities exist in generated data
5. [x] Verify production[date][machine] structure unchanged
6. [x] Run existing tests: `pytest tests/` - no regressions (128/134 passing)

---

### PR15: Aggregation Function & Backward Compatibility - COMPLETED
**Status**: COMPLETE (Merged 2025-11-12)
**Priority**: Critical
**Estimated Effort**: 6-8 hours
**Branch**: `feature/pr15-aggregation`
**Commit**: 7ea3f87 - "feat(aggregation): Add batch-to-production aggregation for backward compatibility (PR15)"
**Pull Request**: https://github.com/willkmacdonald/azure-factory-demo/pull/2

#### Goal
Implement aggregate_batches_to_production() to derive production[date][machine] from batches, ensuring backward compatibility with existing metrics and frontend.

#### Code Review Results
**Rating**: Excellent (production quality)
- Successfully implemented aggregate_batches_to_production() function with full backward compatibility
- Groups batches by date and machine, aggregates all metrics correctly
- Sums parts_produced, good_parts, scrap_parts across batches
- Calculates scrap_rate as percentage with proper division-by-zero handling
- Aggregates quality_issues from all batches preserving full context
- Estimates uptime/downtime from batch durations (simplified for demo)
- Aggregates shift-level metrics (Day/Night) correctly
- Tracks batch IDs in new batches[] field for traceability linkage
- Updated generate_production_data() to use batch generation + aggregation flow
- production_batches[] is now SOURCE OF TRUTH, production[date][machine] is DERIVED
- Comprehensive test coverage: 9 new integration tests, all passing
- All existing tests still pass (160/167 passing, 7 pre-existing unrelated failures)
- Backward compatibility confirmed: existing metrics.py functions work unchanged

#### Files Created/Modified
- **Modified**: shared/data.py (+185 lines) - Added aggregate_batches_to_production() function
- **Modified**: shared/data.py (generate_production_data) - Integrated aggregation into data flow
- **Created**: tests/test_aggregation.py (368 lines) - Comprehensive integration tests

#### Tasks Completed
- [x] Create aggregate_batches_to_production() function in shared/data.py
- [x] Implement quality metrics aggregation from batches
- [x] Implement shift aggregation from batches
- [x] Update generate_production_data() to use batch generation + aggregation
- [x] Test aggregated data matches expected format
- [x] Test existing shared/metrics.py functions still work (manual verification)
- [x] Add integration tests for batch → production aggregation (9 comprehensive tests)

#### Acceptance Criteria Met
- [x] aggregate_batches_to_production() produces production[date][machine] structure
- [x] Aggregated metrics match batch-level data (totals, scrap calculations)
- [x] Existing metrics.py functions work unchanged (backward compatible)
- [x] Existing backend API responses unchanged (structure maintained)
- [x] Existing frontend displays work unchanged (structure maintained)
- [x] All tests pass (9/9 new tests, 160/167 existing tests)
- [x] No regressions in existing functionality
- [x] Data generation flow: batches first, production derived
- [x] New traceability field: production[date][machine].batches[] links to batch IDs

---

## Planned PRs (In Priority Order)

### PR16: Planted Scenarios & Data Realism
**Priority**: High
**Estimated Effort**: 6-8 hours

#### Goal
Plant demonstrable scenarios (quality spike from bad supplier, breakdown affecting orders) and add data realism (supplier quality correlation, serial number tracking).

#### Tasks
- [ ] Plant Scenario 1: Day 15 quality spike traced to Supplier X bad material lot
  - **Priority**: High
  - **Effort**: Medium (2-3hrs)
  - **Context**: Create demonstrable backward trace scenario
  - **Logic**: Generate specific bad lot on Day 15, ensure batches using it have quality issues, link to supplier

- [ ] Plant Scenario 2: Day 22 machine breakdown affecting customer orders
  - **Priority**: High
  - **Effort**: Medium (2-3hrs)
  - **Context**: Create demonstrable forward trace scenario
  - **Logic**: Machine breakdown on Day 22 causes missed order due dates, show which customers affected

- [ ] Add supplier quality rating correlation with defect rates
  - **Priority**: High
  - **Effort**: Medium (1-2hrs)
  - **Context**: Realistic data - suppliers with lower quality_rating cause more defects
  - **Logic**: When assigning quality issues, bias toward lower-rated suppliers' material lots

- [ ] Add serial number tracking with simple ranges
  - **Priority**: High
  - **Effort**: Medium (1-2hrs)
  - **Context**: Track serial number ranges in batches (e.g., "SN-001 to SN-120")
  - **Logic**: Sequential serial assignment, non-overlapping ranges per batch

- [ ] Add quarantine recommendations logic
  - **Priority**: Medium
  - **Effort**: Medium (1-2hrs)
  - **Context**: Flag material lots for quarantine when multiple quality issues link to same lot
  - **Logic**: If lot appears in >3 quality issues, recommend quarantine

- [ ] Document planted scenarios in README or new SCENARIOS.md
  - **Priority**: Medium
  - **Effort**: Quick (<1hr)
  - **Context**: Document how to demonstrate traceability scenarios
  - **Example**: "Navigate to Day 15 quality issues → Trace backward → See Supplier X's bad lot"

- [ ] Add tests for planted scenarios
  - **Priority**: High
  - **Effort**: Medium (1-2hrs)
  - **Context**: Verify planted scenarios exist in generated data
  - **Tests**: Day 15 has quality spike, Day 22 has affected orders, quarantine flags set

- [ ] Add data quality validation
  - **Priority**: Medium
  - **Effort**: Medium (1-2hrs)
  - **Context**: Validate data integrity (no orphaned references, totals add up)
  - **Tests**: All order_ids valid, all lot_numbers valid, serial ranges non-overlapping

#### Acceptance Criteria
- Day 15 quality spike demonstrable: trace backward finds specific supplier's bad lot
- Day 22 breakdown demonstrable: trace forward shows affected customer orders
- Supplier quality ratings correlate with defect rates (realistic)
- Serial number ranges assigned to all batches
- Quarantine recommendations flagged for suspect lots
- Scenarios documented with step-by-step demonstration instructions
- Data integrity validated (no broken references)
- All tests pass

---

## Backlog (Phase 2 - Backend API)

### PR17: New Traceability API Endpoints
**Priority**: High
**Estimated Effort**: 8-10 hours

#### Goal
Add new REST API endpoints for traceability queries (suppliers, lots, orders, batches).

#### Tasks (Summary - Will expand when starting PR)
- [ ] Create backend/src/api/routes/suppliers.py
- [ ] Add GET /api/suppliers - list suppliers with quality metrics
- [ ] Add GET /api/suppliers/{supplier_id} - supplier details
- [ ] Add GET /api/suppliers/{supplier_id}/quality - defects by supplier
- [ ] Add GET /api/suppliers/{supplier_id}/lots - material lots from supplier
- [ ] Create backend/src/api/routes/traceability.py
- [ ] Add GET /api/traceability/backward/{issue_id} - backward trace
- [ ] Add GET /api/traceability/forward/{supplier_id} - forward trace
- [ ] Add GET /api/traceability/lot/{lot_number} - lot impact analysis
- [ ] Add GET /api/traceability/serial/{serial} - serial number trace
- [ ] Create backend/src/api/routes/orders.py
- [ ] Add GET /api/orders - list customer orders
- [ ] Add GET /api/orders/{order_id} - order details
- [ ] Add GET /api/orders/{order_id}/quality - quality issues for order
- [ ] Register new routes in backend/src/api/main.py
- [ ] Add async file operations with aiofiles (FastAPI requirement)
- [ ] Add comprehensive error handling and logging
- [ ] Add tests for all endpoints

#### Acceptance Criteria
- All endpoints return valid responses
- Backward trace finds supplier from quality issue
- Forward trace finds quality issues from supplier
- Lot trace shows impact on batches and orders
- Serial trace finds batch and order for serial number
- Error handling for invalid IDs (404 responses)
- Logging for all operations
- All tests pass

---

### PR18: Enhanced Quality Metrics API
**Priority**: High
**Estimated Effort**: 4-6 hours

#### Goal
Enhance existing GET /api/metrics/quality with traceability filters and cost impact calculations.

#### Tasks (Summary - Will expand when starting PR)
- [ ] Add query parameters to GET /api/metrics/quality
- [ ] Add supplier_id filter parameter
- [ ] Add lot_number filter parameter
- [ ] Add order_id filter parameter
- [ ] Add root_cause_category filter parameter
- [ ] Implement cost_impact calculations (scrap costs by supplier)
- [ ] Implement quarantine recommendations API
- [ ] Add aggregation by supplier/lot/order
- [ ] Add tests for enhanced filtering
- [ ] Update API documentation

#### Acceptance Criteria
- Can filter quality issues by supplier_id
- Can filter quality issues by lot_number
- Can filter quality issues by order_id
- Can filter quality issues by root_cause_category
- Cost impact calculated correctly (scrap + rework + downtime costs)
- Quarantine recommendations returned for suspect lots
- Complex queries work (e.g., "all defects from Supplier X affecting Order Y")
- All tests pass

---

## Backlog (Phase 3 - Frontend - Optional)

### PR19: TypeScript Interfaces & API Client
**Priority**: Medium (Frontend optional for demo)
**Estimated Effort**: 3-4 hours

#### Tasks (Summary)
- [ ] Add TypeScript interfaces to frontend/src/types/api.ts
- [ ] Add Supplier, MaterialLot, Order, ProductionBatch interfaces
- [ ] Enhance QualityIssue interface with traceability fields
- [ ] Add API client functions to frontend/src/services/api.ts
- [ ] Add getSuppliers(), getSupplierQuality(), etc.
- [ ] Add traceBackward(), traceForward(), traceLot() functions
- [ ] TypeScript compilation succeeds

---

### PR20: Supplier Quality Dashboard
**Priority**: Medium
**Estimated Effort**: 6-8 hours

#### Tasks (Summary)
- [ ] Create frontend/src/pages/SuppliersPage.tsx
- [ ] Create frontend/src/components/suppliers/SupplierCard.tsx
- [ ] Create frontend/src/components/suppliers/SupplierQualityReport.tsx
- [ ] Add supplier list view with quality ratings
- [ ] Add drill-down: Supplier → Material lots → Affected batches
- [ ] Add route /suppliers to App.tsx
- [ ] Dashboard displays realistic supplier data

---

### PR21: Material Lot Tracking View
**Priority**: Medium
**Estimated Effort**: 6-8 hours

#### Tasks (Summary)
- [ ] Create frontend/src/pages/MaterialLotsPage.tsx
- [ ] Create frontend/src/components/lots/MaterialLotSearch.tsx
- [ ] Create frontend/src/components/lots/LotImpactAnalysis.tsx
- [ ] Add material lot search/filter interface
- [ ] Add impact analysis: "Lot used in X batches, affecting Y orders, with Z defects"
- [ ] Add quarantine status visualization
- [ ] Can trace defect to source material lot through UI

---

### PR22: Order Impact View
**Priority**: Medium
**Estimated Effort**: 6-8 hours

#### Tasks (Summary)
- [ ] Create frontend/src/pages/OrdersPage.tsx
- [ ] Create frontend/src/components/orders/OrderCard.tsx
- [ ] Create frontend/src/components/orders/OrderQualityReport.tsx
- [ ] Add customer order list with quality metrics
- [ ] Add order detail: Show batches contributing to order, quality issues, affected serials
- [ ] Can see which customer orders contain defective parts

---

## Data Volume Estimates

| Entity | Count | Size per Entry | Total Size |
|--------|-------|----------------|------------|
| Suppliers | 5-10 | ~200B | ~2KB |
| Materials Catalog | 15-20 | ~200B | ~4KB |
| Material Lots | 20-30 | ~300B | ~9KB |
| Orders | 10-15 | ~400B | ~6KB |
| Production Batches | ~540 | ~200B + quality issues | ~120KB |
| Aggregated Production | ~180 entries | ~150B | ~30KB |
| **Total** | | | **~170KB** |

**Conclusion**: Data volume manageable for JSON storage. No database required for demo.

---

## Testing Strategy

### Unit Tests (Per PR)
- **Pydantic Models**: Validate fields, types, constraints
- **Data Generators**: Verify output structure, counts, relationships
- **Aggregation**: Verify derived metrics match batch totals
- **API Endpoints**: Verify responses, error handling, filtering

### Integration Tests (After PR15)
- **End-to-end**: Generate data → Validate all relationships → Test queries
- **Backward Compatibility**: Existing metrics.py functions work unchanged
- **API Integration**: Generate data → API calls → Validate responses

### Scenario Validation (After PR16)
- **Planted Scenarios**: Verify demonstrable traces work as documented
- **Data Integrity**: No orphaned references, totals add up, no duplicate serials

### Manual Testing (Per PR)
- **Small Test Dataset**: 2 days, 2 machines, verify visually
- **Full Dataset**: 30 days, 6 machines, verify performance acceptable
- **API Testing**: Postman/curl for all endpoints

---

## Key Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Breaking existing metrics | High | Medium | Keep production[date][machine] as derived view; test thoroughly |
| Data generation bugs | High | Medium | Build incrementally (PR13 → PR14 → PR15); validate at each step |
| Data consistency issues | Medium | Medium | production_batches[] is single source of truth; add validation |
| File size growth | Low | Low | Monitor size; 170KB manageable; paginate if needed |
| Frontend breaking changes | Low | Low | Backend backward compatible; frontend updates optional |

---

## Success Criteria (Overall Project)

- [ ] Can answer: "Which supplier's materials cause the most defects?"
- [ ] Can answer: "Which customer orders are affected by this quality issue?"
- [ ] Can answer: "Should we quarantine material lot X?"
- [ ] Can answer: "What's the cost impact on suppliers?"
- [ ] Can trace defects to specific part serial numbers
- [ ] Existing dashboard/metrics continue working (no regressions)
- [ ] API endpoints tested and documented
- [ ] Planted scenarios demonstrable in < 5 minutes

---

## Dependencies

### Python Backend
- **Existing**: pydantic, fastapi, aiofiles
- **New**: None (all dependencies already installed)

### React Frontend (Phase 3 - Optional)
- **Existing**: react, react-router-dom, @mui/material, axios
- **New**: None (all dependencies already installed)

---

## Next Steps

1. **Review this plan** - Confirm approach and PR structure
2. **Create PR13 branch** - `git checkout -b feature/pr13-traceability-models`
3. **Start PR13 implementation** - Begin with Supplier Pydantic model
4. **Daily progress updates** - Track completed tasks
5. **PR13 completion** - Run tests, validate, commit
6. **Run pr-reviewer** - Code quality check before merge
7. **Update this plan** - Mark PR13 complete, start PR14

---

## Notes

- **Demo Focus**: Prioritize demonstration value over production robustness
- **Incremental Implementation**: Each PR independently testable, no breaking changes
- **Backend First**: PRs 13-18 deliver core traceability capability
- **Frontend Optional**: API-level demo may be sufficient; frontend nice-to-have
- **Clear Context Between PRs**: Save tokens by clearing context after each PR review
- **Use Agents**: Explore for codebase familiarization, context7 for library docs, pr-reviewer for code quality

---

**Ready to start PR13?** Let's build the foundation!
