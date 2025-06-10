To use the `Kyra` command line tool on Windows:

1. Install the project in editable mode:
   ```cmd
   pip install -e .
   ```

2. Ensure the directory where pip installs scripts is in your `%PATH%`.
   For a typical user install this is:
   `%APPDATA%\Python\Scripts`
   (or the path printed by `pip -V`).

With that setup you can run commands such as:
```cmd
Kyra open youtube
```
which invokes the assistant on the provided text.
