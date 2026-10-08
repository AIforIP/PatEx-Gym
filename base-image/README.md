# Codex harness image

This release contains one prebuilt Linux/amd64 image. It is stored with Git LFS.

```bash
git lfs pull
zstd -dc base-image/patex-codex-harness-amd64.tar.zst | docker load
```

The resulting tag is `patex-codex-harness:latest`. It contains no Elasticsearch data,
source corpus, embedding weights, or model credentials.
