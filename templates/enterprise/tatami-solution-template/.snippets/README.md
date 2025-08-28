# tatami-snippets

> To be used as a submodule only, currently used by [tatami-mod-template](https://git.cglcloud.com/tat-ops/tatami-mod-template) and all derived repositories. Can be added manually to any other repository.

## Snippets

This repository exposes a set of code *snippets* to reproduce specific recurring and useful blocks of code.

You can add new snippets by invoking the snippets script from the root folder of your repository:

```bash
.snippets/add.sh < path pointing to the root folder of the repository, can be specified with a relative path >
```

When made available from a repository created via [tatami-mod-template](https://git.cglcloud.com/tat-ops/tatami-mod-template), a custom Visual Studio Code command called `TATami-snippets` to launch the same script will be available.

The script will ask you to pick a scaffolding option, followed by the name of a prefix that will be added to all the names of the generated files. We recommend you keep such name short and without whitespace. Names like `test01` or `downloader` will do.

Snippets are simple and self-describing, normally containing enough comments to illustrate what they achieve and how they should be used or filled.

Feel free to contribute more snippets to this repository, you are just one PR away from sharing more awesomeness!
