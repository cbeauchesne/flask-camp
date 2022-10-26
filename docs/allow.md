To allow both authenticated and anonymous users, you must do :

```python
    @allow("anonymous", "authenticated")
```