# What's next?

1. Open the `main.py` file and add your code to it. You are free to add more files and import them in `main.py`.
2. If necessary, add libraries you need to use in `requirements.txt`.
3. Go to the Debug section of VS Code and make sure you select the `Debug` profile.
4. Perform any debug cycle you need. Just press F5 while having `main.py` open to load your code and attach the debugger to it, then use the `TATami-trigger` command from the palette (`CTRL`+`SHIFT`+`P`) to trigger more executions from within the debugger. Features like breakpoints and watch entries will now work.
5. Once ready to deploy, and assuming you want to use the AWS Lambda runtime, just remember to move to the root of your repository, open the *snippets* (command `TATami-snippets`) and select `invoke-modules\tatami-comp-activator-lambda`. This will create a file with the invocation of the right Terraform module to deploy your code as a Lambda function. The snippet will describe how you should fill available arguments via code comments.
