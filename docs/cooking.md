## What is a cooker?

It's a function that make transformation to a document JSON object, just before sending it. 

## Why is it usefull?

Document served by the API are by default the document produced by the database. But one common need is to modify this document before serving it. For instance, you may want to :

* transform some markdown to HTML
* add another documment inside the response, because it's needed for the renderingm and you don't wont the UI make several call to the API to render a single page

## How to use it ?
You need to provide a cooking function using the `@app.cooker` decorator : 

```python
from cms import Application

app = Application()

@app.cooker
def my_cooker(document, get_document):  # pylint: disable=unused-argument
    # here you can modify the document
    document["cooked"] = "Some new info not present directly in base document"
```

## How to use it?

`document` is a python dict, as it would be send to a request. You can directly modify it. The function returns nothing

```
document
    id              : The id of the document
    namespace       : Document's namespace
    last_version_id : The current last version of the document
    version_id      : The version of the document. If version_id==last_version_id, it means that this obkect is the current version of the document
    comment         : Modification's omment of the that mades this versions
    timestamp       : Modification's timestamp
    user            : User who made this document
    protected       : Boolean, if the document is protected
    hidden          : Boolean, if this version is hidden
```

`get_document` is a function that take a document id, and returns the non-cooked version of this document (or `None` if it dosn't exists).

## But keep in mind some rules to avoid any trouble

* Do not modify `document["data"]`. Otherwise, your modification will be present when you try to modify a document, and you will need to clean it. A good way to to this is to put any extra data in `document["cooked"]`.
* Do not put any dynamic content. It's cooked only once, and saved in memory cache: `document["cooked"] = datetime.now()  # bad`
* Even if you could get other documents using some other function of `app`, `get_document` provided in argument will memorize which documents has been requested to cook your document. This informations is saved, and will be used later to clean the memory cache if any of those document is modified. So use it, otherwise you may corrupt your memory cache!