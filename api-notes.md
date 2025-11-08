# Web URL

https://openrouter.ai/models?fmt=cards&supported_parameters=tools

&supported_parameters=tools

Shows:

- Model name (readable)
- Model ID (API) 
- Vendor 
- Context 
- Input tokens USD/M
- Output tokens USD/M
- Description 
- Model params 

# Get All Models

curl https://openrouter.ai/api/v1/models \
     -H "Authorization: Bearer <token>"

# API Doc

https://openrouter.ai/docs/api-reference/models/get-models

---

# Response Units

Note: frontend prices and those returned by the API may look slightly different as the same model endpoints have different pricing based upon the underlying inference provider. 

API response prices are expressed *per token*. In order to convert them to the conventionally used comparison metric of USD per *million* tokens, the values need to be multiplied by one million (see: script).