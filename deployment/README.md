# Deploy to cluster

## Fetch dependencies
To download helm dependencies, run the following command:

```shell
helm dependency build deployment/poker-chart
```

## Deploy
For an upgrade (or install):

```shell
helm upgrade --install --render-subchart-notes poker deployment/poker-chart
```
