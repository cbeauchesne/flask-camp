One common need is to define schema conditionnaly. You need to :

1. define a document type property on all your document
2. apply a schema conditionnaly, based on that property

*base schema* : be sure 
```json
{
  "properties": {
    "data": {
      "type": {
        "enum": ["outing", "route"]
      }
    }
  }
}
```

*outing schema*
```json
{
  "properties": {
    "data": {
      "if": {
        "properties": { "type": { "const": "outing" } },
        "required": ["type"]
      },
      "then": {
        "properties": {
          "value": { "type": "string" },
          "rating": { "$ref": "entities/rating.json" },
          "type": { "const": "outing" }
        },
        "required": ["value", "rating", "type"],
        "additionalProperties": false
      }
    }
  }
}```


*route schema*
```json
{
  "properties": {
    "data": {
      "if": {
        "properties": { "type": { "const": "route" } },
        "required": ["type"]
      },
      "then": {
        "properties": {
          "type": { "const": "route" }
        }
      }
    }
  }
}```

