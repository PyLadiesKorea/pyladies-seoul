# Test Code Writing Guidelines

## 1. Factory Usage Principles

### ✅ Recommendations
- **Use Factories**: Generate all test data through factories
- **Clear Dependencies**: Define necessary relationships clearly in factories
- **Reusability**: Define common factories in `conftest.py`

### ❌ Things to Avoid
- Direct model manager usage (`Model.objects.create()`)
- Hardcoded test data
- Duplicated setup code

## 2. Factory Writing Guidelines

### Basic Factory Structure
```python
class MyModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MyModel

    # Basic fields
    name = factory.Faker("word")
    description = factory.Faker("sentence")
    
    # Relationship fields
    user = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory)
    
    # Using sequences
    code = factory.Sequence(lambda n: f"CODE_{n}")
    
    # Default values
    is_active = True
```

### Factory Usage
```python
# ✅ Correct usage
user = UserFactory.create()  # Save to DB
user = UserFactory.build()   # Don't save

# ❌ Incorrect usage
user = UserFactory()  # Only create instance, not saved
user = User.objects.create_user(...)  # Direct model manager usage
```

## 3. Test Structure Guidelines

### Using Common Base Classes
```python
class BaseTestCase:
    """Common test base class"""
    
    def setup_method(self):
        """Setup that runs automatically for each test"""
        self.client = APIClient()
        self.user = UserFactory.create()
        self.client.force_authenticate(user=self.user)

@pytest.mark.django_db
class TestMyAPI(BaseTestCase):
    def test_something(self):
        # Test logic
        pass
```

### Test Method Naming
```python
def test_action_expected_result(self):
    """Name in action_expected_result format"""
    pass

# Examples
def test_create_user_returns_201(self):
def test_invalid_email_returns_400(self):
def test_unauthorized_access_returns_401(self):
```

## 4. Test Data Generation Patterns

### Simple Object Creation
```python
# ✅ Using factories
user = UserFactory.create()
homework = HomeworkFactory.create(user=user)

# ❌ Direct creation
user = User.objects.create_user(...)
homework = Homework.objects.create(...)
```

### Complex Relationship Creation
```python
# ✅ Factory chaining
homework = HomeworkFactory.create(
    user=UserFactory.create(),
    course=CourseFactory.create()
)

# ✅ Using SubFactory
class HomeworkFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Homework
    
    user = factory.SubFactory(UserFactory)
    course = factory.SubFactory(CourseFactory)
```

### Creating Multiple Objects
```python
# ✅ Using factories
users = UserFactory.create_batch(3)
homeworks = HomeworkFactory.create_batch(5, user=user)

# ❌ Direct creation in loops
for i in range(3):
    User.objects.create_user(...)
```

## 5. Test Case Writing Patterns

### AAA Pattern (Arrange, Act, Assert)
```python
def test_user_creation(self):
    # Arrange (Setup)
    user_data = {
        "username": "testuser",
        "email": "test@example.com"
    }
    
    # Act (Execute)
    response = self.client.post("/api/users/", user_data)
    
    # Assert (Verify)
    assert response.status_code == 201
    assert User.objects.count() == 1
```

### Edge Case Testing
```python
def test_invalid_data_handling(self):
    """Test handling of invalid data"""
    invalid_data = {"email": "invalid-email"}
    
    response = self.client.post("/api/users/", invalid_data)
    
    assert response.status_code == 400
    assert "email" in response.data["errors"]
```

## 6. Mock Usage Guidelines

### Mocking External Services
```python
@patch("k6.common.services.upload_to_cdn")
def test_file_upload(self, mock_upload):
    # Mock setup
    mock_upload.return_value = "https://example.com/file.jpg"
    
    # Test execution
    response = self.client.post("/api/upload/", data)
    
    # Verification
    assert response.status_code == 200
    mock_upload.assert_called_once()
```

## 7. Performance Considerations

### Preventing N+1 Problems
```python
# ✅ Using select_related, prefetch_related
users = User.objects.select_related('profile').prefetch_related('posts').all()

# ❌ N+1 query occurrence
users = User.objects.all()
for user in users:
    print(user.profile.name)  # Additional query occurs
```

### Test Data Optimization
```python
# ✅ Create only what's needed
user = UserFactory.create()
post = PostFactory.create(user=user)

# ❌ Creating unnecessary data
users = UserFactory.create_batch(100)  # Unnecessary for test
```

## 8. File Structure

```
tests/
├── __init__.py
├── conftest.py          # Factories and common fixtures
├── test_models.py       # Model tests
├── test_views.py        # View/API tests
├── test_services.py     # Business logic tests
└── test_utils.py        # Utility function tests
```

## 9. Verification Checklist

- [ ] Use factories to generate test data
- [ ] Remove duplicated setup code (use base classes)
- [ ] Clear test method naming
- [ ] Follow AAA pattern
- [ ] Include edge case tests
- [ ] Use mocks appropriately
- [ ] Consider performance (prevent N+1 problems)
- [ ] Ensure test independence
