# Publishing

The GitHub release already contains a Python wheel and an npm tarball. Registry publishing is a one-time account setup.

## PyPI

1. Create the `walkthrough` project on PyPI.
2. Add a trusted publisher with owner `iambiniyam`, repository `walkthrough`, workflow `publish.yml`, environment `pypi`.
3. Add the GitHub variable `PUBLISH_PYPI=true`.
4. Run the `publish-pypi` workflow manually, or publish a new release.

## npm

1. Create `walkthrough-render` on npm.
2. Configure npm trusted publishing for owner `iambiniyam`, repository `walkthrough`, workflow `npm-publish.yml`.
3. Add the GitHub variable `PUBLISH_NPM=true`.
4. Run the `publish-npm` workflow manually, or publish a new release.

## Direct install

```bash
pip install https://github.com/iambiniyam/walkthrough/releases/download/v0.1.2/walkthrough-0.1.2-py3-none-any.whl
pnpm add https://github.com/iambiniyam/walkthrough/releases/download/v0.1.2/walkthrough-render-0.1.0.tgz
```
