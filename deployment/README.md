# Create Docker Secret
If your token is in your clipboard, and you have pbpaste:

```shell
kubectl create secret docker-registry ghrcred \
  --docker-server=ghcr.io \
  --docker-username=BlackthornYugen \
  --docker-password=$(pbpaste) \
  --docker-email=email@email.email
```

# Deploy to cluster

kubectl apply -f deployment/k8s