# Development workflow

A solution module, like the one developed here, will use Terraform code to deploy components, of which some are likely to deploy executable resources on AWS. Those resources will be part of an end-to-end solution either for a business requirement or for transversal capabilities. Examples of such type of resources are:

- AWS Lambda
- AWS Batch
- AWS ECS
- ...

For the moment only AWS Lambda is supported, but this will change in the near future.

All AWS runtime environments we support as part of TATami use containers to run their workloads, therefore this module will need to deliver proper container images to be executed on the runtime of choice. We'll see later how this is achieved.

## Where does my code go?

Fill the [main.tf](main.tf), [variables.tf](variables.tf) and [locals.tf](locals.tf) files appropriately to deliver the logic of your module.

## Submodules

This repository references other repositories as *git submodules*. This way it is always possible to update tools like *scaffoldings*, *snippets*, and configuration settings for the GHS Sandbox.

Please do update them regularly to always have the respective latest versions. You can do that from the Source Control section of Visual Studio Code, where you can pull the latest version of each of the listed submodules using the respective menus. For example, you can perform this sequence of actions:

- `...` menu for each submodule
- `Pull, Push`
- `Sync`

Similarly, you can perform the same by opening a terminal window at the root of the repository, and then launching the following commands:

```bash
git submodule update --init --recursive --progress
git submodule update --recursive --remote --merge --progress
```

## Scaffolding

This repository exposes a set of *scaffolding* setups to enable specific recurring configurations for testing and deploying your modules. Those setups change according to the type of module you picked during the initialization phase (*passive*, *active*, *solution*).

You can add new configurations by invoking the scaffolding script from the root folder of your repository:

```bash
.scaffolding/add.sh
```

The script will ask you to pick a scaffolding option, followed by the name of the folder that will contain the configuration. We recommend you keep such name short and without whitespace. Names like `test01` or `downloader` will do.

It's also possible and easier to launch the same script via the `TATami-scaffolding` task, as explained [in the last section of this doc](#visual-studio-code-tasks).

Let's now go through some of the supported configurations for the current type of module.

### How do I test that my code works and deploys correctly?

You can prepare multiple, dedicated test folders to validate that your code works and deploys correctly.

The *executable* configurations, located under `run`, allow you to build actual, containerized solution components to be deployed remotely, both on GHS Sandbox and GHS Automated, and enable you to execute them locally for debugging. The same assets can be used to build *test* container images to be deployed on GHS Sandbox for validation of your work.

The *deployment* configurations, located under `tests/terraform/cases`, target the GHS Sandbox environment. These deployments are created as isolated areas inside a *Terraform state file* dedicated to TAT. Every folder in every module *and for every user* gets a dedicated space. This implies that *safe and concurrent development can happen across modules and developers*.

### Visual Studio Code tasks

Visual Studio Code allows the definition of tasks that can be easily discovered and executed via its command palette (`CTRL`+`SHIFT`+`P`, then select the **Tasks: Run Task** command).

This repository defines a few of such commands to launch. Here you have them:

| Task identifier | Description | Script | Notes |
|--|--|--|--|
| `TATami-init` | Perform the repository initialization. | `./init.sh` | Working directory set to the repository root. |
| `TATami-scaffolding` | Prepares a set of coordinated files to provide a full feature.  | `.scaffolding/add.sh`| Working directory set to the repository root. |
| `TATami-snippets` | Creates a set of coordinated files solving a recurrent problem. | `.snippets/add.sh` | Working directory set to folder containing the currently active file in the editor. |
| `TATami-trigger` | Special trigger to launch a script with the AWS Lambda Runtime Interface Emulator inside a debug session. | `trigger.sh` | Working directory set to folder containing the currently active file in the editor. |
| `TATami-tf-aws-configure` | Configures the AWS credentials to be used with the Terraform commands. | `../../commands/aws_configure.sh` | - |
| `TATami-tf-init` | Initialized the current folder as a Terraform module. | `../../commands/init.sh` | Working directory set to folder containing the currently active file in the editor. |
| `TATami-tf-plan` | Performs a `terraform plan` command form the current folder. | `../../commands/plan.sh` | Working directory set to folder containing the currently active file in the editor. |
| `TATami-tf-apply` | Performs a `terraform apply` command form the current folder. | `../../commands/apply.sh` | Working directory set to folder containing the currently active file in the editor. |
| `TATami-tf-destroy` | Performs a `terraform destroy` command form the current folder. | `../../commands/destroy.sh` | Working directory set to folder containing the currently active file in the editor. |
