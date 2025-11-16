# Factory Agent - Development Roadmap

**Last Updated**: 2025-11-15
**Project Goal**: Integrated demo of Azure migration + Supply Chain Traceability
**Current Phase**: Phase 2 - Backend Integration

---

## Vision

Build a comprehensive Industry 4.0 factory monitoring demo that showcases:
1. **Full-Stack Development**: Data models → REST API → React UI → Azure deployment
2. **Supply Chain Traceability**: Root cause analysis (quality → supplier) and impact analysis (supplier → orders)
3. **Modern Azure Architecture**: Container Apps, CI/CD, Infrastructure as Code

---

## Milestone Overview

| Phase | Status | Effort | Goal |
|-------|--------|--------|------|
| **Phase 1** | ✅ Complete | - | Backend API + Azure infrastructure |
| **Phase 2** | 🚧 Next Up | 8-12 hours | Merge traceability + API endpoints |
| **Phase 3** | ⏸️ Planned | 18-24 hours | Complete React pages with traceability |
| **Phase 4** | ⏸️ Planned | 6-8 hours | Deploy frontend to Azure |
| **Phase 5** | ⏸️ Planned | 8-12 hours | Polish with demonstrable scenarios |

**Total Remaining**: 40-56 hours (~5-7 weeks at 8-10 hours/week)

---

## Phase 1: Foundation ✅ COMPLETE

### What Was Built
- **FastAPI Backend**: All monitoring endpoints (OEE, scrap, quality, downtime, chat)
- **Azure Infrastructure**: Bicep templates, Container Apps, Container Registry
- **CI/CD Pipeline**: GitHub Actions for backend deployment
- **React Foundation**: Navigation, layout, API client, TypeScript types
- **Testing**: 79+ tests (unit + integration)
- **Traceability Models**: Supplier, MaterialLot, Order, ProductionBatch (on feature branch)

### Key Deliverables
- Backend deployed to Azure Container Apps
- React app running locally with health check
- All tests passing
- Documentation complete

**Completed**: PR6-PR13 (see ARCHIVE-completed-prs.md for details)

---

## Phase 2: Backend Integration 🚧 NEXT UP

**Estimated Effort**: 8-12 hours
**Goal**: Integrate traceability into main branch and expose via REST API

### Tasks

1. **Merge Feature Branch** (2-3 hours)
   - Cherry-pick traceability commits from `feature/pr15-aggregation`
   - Preserve deployment infrastructure (don't merge deletions)
   - Run all tests to verify

2. **Add Traceability API** (6-8 hours)
   - 9 new endpoints in `backend/src/api/routes/traceability.py`
   - Suppliers, batches, orders, backward/forward trace
   - Enhance existing quality/stats endpoints with filters

3. **Testing** (1 hour)
   - pytest for all new endpoints
   - Validate traceability queries

### Success Criteria
- ✅ Feature branch merged into main
- ✅ 9 new API endpoints working
- ✅ All tests passing
- ✅ API docs updated (FastAPI /docs)

### References
- See `MERGE-STRATEGY.md` for detailed merge instructions
- See `implementation-plan.md` Phase 2 for task breakdown

---

## Phase 3: Frontend Complete ⏸️ PLANNED

**Estimated Effort**: 18-24 hours
**Goal**: Complete all React pages with monitoring + traceability features

### Key PRs

**PR14: Machine Status & Alerts** (3-4 hours)
- Machine list view with status indicators
- Alert notification system
- Machine detail page

**PR15: Supplier Traceability Page** (4-5 hours) ⭐ Core Feature
- Batch lookup with visualization
- Supplier impact analysis
- Order status tracking

**PR16: AI Chat Interface** (3-4 hours)
- Chat console with history
- Integration with backend /api/chat
- Suggested prompts

**PR17: Dashboard Enhancements** (4-6 hours)
- Supplier quality scorecard
- Orders overview section
- Clickable links to traceability pages

**PR18: UI Polish** (2-3 hours)
- Loading skeletons
- Improved empty states
- Mobile responsiveness

### Success Criteria
- ✅ All pages functional with real data
- ✅ Traceability workflows demonstrable
- ✅ No console errors
- ✅ Responsive design (desktop + mobile)

---

## Phase 4: Frontend Deployment ⏸️ PLANNED

**Estimated Effort**: 6-8 hours
**Goal**: Deploy React frontend to Azure Container Apps with CI/CD

### Tasks

1. **Verify Docker Build** (1 hour)
   - Test multi-stage Dockerfile
   - Verify Nginx configuration
   - Local testing

2. **Update Infrastructure** (2-3 hours)
   - Update Bicep template for frontend app
   - Configure CORS on backend
   - Environment variables

3. **GitHub Actions** (2-3 hours)
   - Frontend build/push/deploy pipeline
   - Trigger on frontend/ changes
   - Health check verification

4. **E2E Testing** (1-2 hours)
   - Test deployed application
   - Verify all features
   - Document URLs

### Success Criteria
- ✅ Frontend deployed to Azure
- ✅ Backend + Frontend communicating
- ✅ CI/CD working for both
- ✅ All features functional in cloud

---

## Phase 5: Polish & Scenarios ⏸️ PLANNED

**Estimated Effort**: 8-12 hours
**Goal**: Add demonstrable scenarios to showcase traceability in 5-minute demos

### Tasks

1. **Plant Scenarios** (4-6 hours)
   - Day 15 quality spike (bad material lot)
   - Day 22 machine breakdown (delayed orders)
   - Supplier quality correlation

2. **Quarantine Logic** (1-2 hours)
   - Flag suspect material lots
   - Provide recommendations

3. **Documentation** (2-3 hours)
   - DEMO-SCENARIOS.md with step-by-step instructions
   - Update README.md
   - Screenshots/videos

4. **Validation Tests** (1-2 hours)
   - Verify planted scenarios exist
   - Test traceability paths
   - Validate data integrity

### Success Criteria
- ✅ Day 15 demo works (quality → supplier trace)
- ✅ Day 22 demo works (breakdown → orders trace)
- ✅ Demo documentation complete
- ✅ README updated

---

## Optional: Authentication

**Estimated Effort**: 8-10 hours
**When**: Only if demo needs multi-user access or enterprise showcase
**Decision Point**: After Phase 5

### Tasks
- Azure AD/MSAL configuration
- Login/logout UI
- Protected routes
- Backend JWT validation

**Recommendation**: Skip for portfolio demo, add for production deployment

---

## Success Metrics

### Technical Completeness
- [ ] All backend endpoints working (monitoring + traceability)
- [ ] All React pages functional with real data
- [ ] Deployed to Azure (backend + frontend)
- [ ] CI/CD pipelines working
- [ ] All tests passing (unit + integration)
- [ ] 100% type hints (Python + TypeScript)

### Demonstrable Capability
- [ ] 5-minute demo: Quality issue → Supplier trace
- [ ] 5-minute demo: Supplier → Affected orders trace
- [ ] 5-minute demo: Order fulfillment status
- [ ] Dashboard shows comprehensive metrics
- [ ] AI chat answers traceability questions

### Documentation
- [ ] README.md explains features
- [ ] DEMO-SCENARIOS.md provides demo scripts
- [ ] API documentation complete (FastAPI /docs)
- [ ] Code well-commented
- [ ] Architecture documented

---

## Timeline Projections

### Conservative (8-10 hours/week)
- Week 1-2: Phase 2 (Backend Integration)
- Week 3-5: Phase 3 (Frontend Complete)
- Week 6: Phase 4 (Deployment)
- Week 7: Phase 5 (Polish)
- **Total**: 7 weeks

### Aggressive (15-20 hours/week)
- Week 1: Phase 2 (Backend Integration)
- Week 2: Phase 3 (Frontend Complete)
- Week 3: Phase 4 (Deployment)
- Week 4: Phase 5 (Polish)
- **Total**: 4 weeks

---

## Decision Log

### 2025-11-15: Integrated Approach (Option B)
**Decision**: Pursue integrated migration + traceability in one comprehensive demo

**Rationale**:
- User preference for one strong demo over split demos
- Focus on building traceability end-to-end
- No timeline pressure allows quality over speed
- Showcases full-stack development skills

**Alternative Considered**:
- Option A (Sequential): Finish Azure migration first, then add traceability
- Rejected because user wants to focus on traceability feature

---

## Key Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Merge conflicts in feature branch | Medium | Use MERGE-STRATEGY.md cherry-pick approach |
| Frontend pages too complex | Medium | Build incrementally, test each PR separately |
| Deployment issues | Medium | Test locally first, use existing backend pipeline as template |
| Scenarios not demonstrable | High | Test demo paths explicitly, document step-by-step |

---

## Related Documentation

- **implementation-plan.md**: Detailed task breakdown for upcoming phases
- **ARCHIVE-completed-prs.md**: Specifications for completed PR6-PR13
- **MERGE-STRATEGY.md**: Guide for merging traceability feature branch
- **PR13_SUMMARY.md**: Supply chain models implementation
- **docs/PR14_SUMMARY.md**: ProductionBatch implementation
- **docs/traceability_examples.py**: Example traceability queries

---

**Next Action**: Begin Phase 2 - Backend Integration (see implementation-plan.md for task details)
