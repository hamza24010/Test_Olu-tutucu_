# Test Implementation Plan

## Overview
This plan outlines the steps to establish a robust testing infrastructure for the "Test Oluşturucu" application. The immediate focus is on **Core Logic** and **Database** interactions using `pytest`, ensuring the foundational logic (PDF processing, Question extraction, Data persistence) is verified before moving to complex UI testing.

## Project Type
**Desktop Application (Python)**
*   **Primary Focus:** Backend Logic & Data Layer
*   **Secondary Focus:** UI Logic (mocked/headless where possible)

## Success Criteria
1.  **Infrastructure:** `pytest` installed and configured with coverage reporting.
2.  **Coverage:**
    *   **Core:** PDF extraction and Gemini AI service (mocked) are tested.
    *   **Database:** CRUD operations for Questions/Tests are verified using in-memory databases.
3.  **CI Readiness:** Tests can be run via a single command (`pytest`).

## Tech Stack
*   **Runner:** `pytest` (Standard Python testing framework)
*   **Plugins:**
    *   `pytest-cov` (Coverage reporting)
    *   `pytest-mock` (Mocking external services like Google Gemini)
    *   `pytest-asyncio` (If async operations exist)

## File Structure Plan
```
Test_Olusturucu/
├── tests/                  # Root test directory
│   ├── __init__.py
│   ├── conftest.py         # Global fixtures (DB setup, Mock definitions)
│   ├── unit/               # Unit tests (isolated)
│   │   ├── core/           # Tests for src/core
│   │   │   ├── test_pdf_extractor.py
│   │   │   └── test_gemini_service.py
│   │   └── db/             # Tests for src/db
│   │       └── test_database_manager.py
│   └── integration/        # Integration tests (Core <-> DB)
│       └── test_question_flow.py
```

## Task Breakdown

### Phase 1: Setup & Configuration
| Task ID | Name | Agent | Skills | Dependencies | Implementation Verification |
|O-1| **Dependencies & Config** | `backend-specialist` | `python-patterns` | None | `pytest --version` returns success, `pytest.ini` exists. |
|O-2| **Test Directory Structure** | `backend-specialist` | `bash-linux` | O-1 | Directory `tests/unit` and `tests/integration` exist. |

### Phase 2: Database Testing (Foundation)
| Task ID | Name | Agent | Skills | Dependencies | Implementation Verification |
|DB-1| **DB Fixtures (conftest.py)** | `backend-specialist` | `testing-patterns` | O-2 | Fixture provides a clean in-memory SQLite session. |
|DB-2| **CRUD Unit Tests** | `backend-specialist` | `tdd-workflow` | DB-1 | Tests for Create, Read, Update, Delete questions pass. |

### Phase 3: Core Logic Testing (Mocking AI)
| Task ID | Name | Agent | Skills | Dependencies | Implementation Verification |
|C-1| **Gemini Service Mocks** | `backend-specialist` | `testing-patterns` | O-2 | `GeminiService` can be called in test without hitting real API. |
|C-2| **PDF Extraction Tests** | `backend-specialist` | `clean-code` | O-2 | PDF parser returns expected text from sample PDF. |
|C-3| **Question Parsing Logic** | `backend-specialist` | `tdd-workflow` | C-1 | Tests verify AI response parsing into structured objects. |

### Phase 4: Integration (Optional for V1)
| Task ID | Name | Agent | Skills | Dependencies | Implementation Verification |
|I-1| **Full Flow Test** | `backend-specialist` | `testing-patterns` | DB-2, C-3 | Verify flow: PDF -> Gemini Mock -> DB Save. |

## Phase X: Verification Checklist
- [ ] **Environment**: `pip install pytest pytest-cov pytest-mock` successful.
- [ ] **Configuration**: `pytest.ini` ensures correct python path.
- [ ] **Execution**: `pytest` runs without errors.
- [ ] **Coverage**: Report generated showing >0% coverage on Core/DB modules.
- [ ] **Linting**: Test files pass standard linting checks.
