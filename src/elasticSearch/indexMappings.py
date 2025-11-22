indexMappings = {
  "properties":{
    "scheme_id":{
      "type":"long"
    },
    "site": {
      "type": "keyword"
    },
    "scheme_name":{
      "type":"text",
    },
    "description":{
      "type":"text",
    },
    "scheme_link":{
      "type": "keyword"
    },
    "description_vector":{
      "type":"dense_vector",
      "dims":768,
      "index":True,
      "similarity":"l2_norm"
      # l2_norm is root sum sqaured
    }
  }
}