# Counsel

Counsel is the query tool for [Consul](https://www.consul.io/). As of now it make supports:
 - Querying a service via the **health** endpoint (`/v1/health/service/<service>`).
 - Querying a service via the **query** endpoint (`/v1/query`)

**Note**: this is a hacky tool it's not suggested to be used!

## Examples

### Query a consul service

```
# default server is 127.0.0.1:8500
counsel query -s consul

# specificaly define the consul server
counsel -s http://consul:8500 query -s consul
```

### Jinja Filters

Jinja filters allow you to transform the query results and pick specific data. Vanilla jinja processing is used, though there are two helpers added:

- **split** - splits a string, args: `(string, separator, maxsplit=1)`
- **todict** - converts a *k,v* iterator into a dict.

Let's assume that we make a health query like `counsel health -s node_meta` this will output the following JSON (it's not the full output!):

```json
[
    {
        "Node": {
            "Address": "10.68.9.179",
        },
        "Service": {
            "Service": "node_meta",
        }
    },
    {
        "Node": {
            "Address": "10.68.9.47",
            "Node": "8980304e5ea5",
        },
        "Service": {
            "Service": "node_meta",
        }
    },
    {
        "Node": {
            "Address": "10.68.9.74",
            "Node": "e56f05b71d98",
        },
        "Service": {
            "Service": "node_meta",
        }
    }
]
```

Jinja filters allow you to transform the result so that you can pick only the required items. For example, let's say we just need to grab the node addresses. This can be achieved by providing a Jinja filter:

```bash
counsel health -s node_meta -f '{{Node.Address}}'

# outputs =>
[
    "10.68.9.179",
    "10.68.9.47",
    "10.68.9.74"
]
```

There are to output formatters *oneline* and *multiline* which print the result in one line or in several lines respectively. For example applying `--oneline` will format the result in the following way:

```bash
counsel health -s node_meta --oneline -f '{{Node.Address}}'

# outputs =>
10.68.9.179 10.68.9.47 10.68.9.74
```

### More examples (using todict and split)

Let's assume our service has a colon delimited (*"k:v"*) list of tags specified. We want to get instance_id for all nodes having a tag "class:pio":

```
counsel health -s node_meta --multiline -f '{{Node.Address}}' "{% set tags = Service.Tags|map('split', ':')|todict %}{{ tags.instance_id if tags.class == 'pio' }}"
# outputs =>
i-091a147b64937450b
```
