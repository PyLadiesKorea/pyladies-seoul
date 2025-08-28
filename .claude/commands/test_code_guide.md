# Test Code Writing Guide

<test_code_principles>
1. **Every function and class must be covered by tests.**
2. **Test function names should start with `test_`.**
3. **Tests must be independent and repeatable, not relying on external state.**
4. **Failure and exception cases must be included.**
5. **Test coverage of at least 80% is recommended.**
6. **Automated test scripts and CI integration are strongly encouraged.**
7. **Apply the FIRST principle:**
   - **Fast**: Tests should run quickly.
   - **Isolated**: Each test should be independent from others.
   - **Repeatable**: Tests should produce the same results every time.
   - **Self-Validating**: Tests should have clear pass/fail outcomes.
   - **Timely**: Write tests as early as possible, ideally alongside production code.
</test_code_principles>

<tdd_principles>
**Test-Driven Development (TDD) Principles**
- Always write tests before implementing production code.
- Follow the Red-Green-Refactor cycle:
  1. **Red**: Write a failing test for a new feature or bug fix.
  2. **Green**: Write the minimal code necessary to make the test pass.
  3. **Refactor**: Clean up the code while ensuring all tests still pass.
- Repeat this cycle for each new functionality.
</tdd_principles>

<test_code_process>
1. Identify the functionality to implement.
2. **Write a test for the new functionality (TDD).**
3. Run the test and confirm it fails (Red).
4. Implement the minimal code to pass the test (Green).
5. Refactor the code for clarity and maintainability.
6. Repeat for each new feature or bug fix.
</test_code_process>

<tdd_example>
```python
# Step 1: Write the test first (Red)
def test_add_positive_numbers():
    assert add(2, 3) == 5

# Step 2: Implement minimal code (Green)
def add(a: int, b: int) -> int:
    return a + b

# Step 3: Refactor if needed (Refactor)
# (In this simple case, the code is already clean)
```
</tdd_example>

<test_code_example>
```python
import pytest

def add(a: int, b: int) -> int:
    return a + b

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0
```
</test_code_example>

<django_test_example>
```python
from django.test import TestCase
from .models import MyModel

class MyModelTestCase(TestCase):
    def setUp(self):
        MyModel.objects.create(name="Test", value=123)

    def test_model_str(self):
        obj = MyModel.objects.get(name="Test")
        self.assertEqual(str(obj), "Test")
```
</django_test_example>

<test_coverage_and_automation>
- Use tools like `pytest-cov` or `coverage.py` to measure test coverage.
- Aim for at least 80% coverage, but prioritize meaningful tests over metrics.
- Integrate tests into CI pipelines (e.g., GitHub Actions, GitLab CI, Jenkins).
- Automate test execution on every commit or pull request.
</test_coverage_and_automation>

<test_checklist>
- [ ] Are all major functions/classes covered by tests?
- [ ] Are failure and exception cases tested?
- [ ] Are mocks/fixtures used appropriately?
- [ ] Is test coverage above 80%?
- [ ] Are tests automated in CI?
- [ ] Are test results clearly reported?
- [ ] Are FIRST principles followed?
</test_checklist>

<test_report_format>
## Test Report Example

### Test Name: add function unit test
- **Status**: Passed
- **Environment**: Python 3.10, pytest 7.0
- **Test Cases**: 3
- **Failures**: 0
- **Notes**: Includes edge cases (negative, zero)

### Next Steps
- Add tests for uncovered functions
- Write integration tests
</test_report_format> 