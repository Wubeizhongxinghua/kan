# kan
A tiny tool for reminding if jobs running on shell, or tasks submitted on [Beijixing](http://www.aais.pku.edu.cn/clshpc/) finished via email or webhook.

### New version features

+ 0.2
> Monitoring shell jobs supported!
+ 0.3
> Reminds based on webhook supported!
+ 0.4
> `kan send` is now provided, where you can strightly send messages to your config address

### Requirements
+ Linux or UNIX system
+ Python 3 installed
+ `click`, `toml`, `absl-py` package installed

### Installation

The `kan` python package is in the folder `kan`. You can simply install it from the

```shell
$ pip install .
```
Alternatively, you can also install the package directly from GitHub via

```shell
$ pip install git+https://github.com/Wubeizhongxinghua/kan.git
```

### Usage

+ Config

After installing, you need to config the sender email and the receiver email by

```shell
$ kan set-config \
	-t email \
	-h SMTP_HOST_OF_EMAIL_SERVER \
	-d PORT \
	-u USER_NAME_OF_EMAIL_ACCOUNT \
	-p PASSWD_OR_TOKEN \
	-s SENDER_EMAIL \
	-r RECEIVER_EMAIL \
	CONFIG_NAME
```

Besides, if you want the remind to rely on webhook, you may set:
```shell
$ kan set-config \
	-t webhook \
	-w WEBHOOK_URL \
	CONFIG_NAME
```

You can also use `kan list-config` to list all configs you have created.

To get insight into one specific config, use

```shell
$ kan list-config -c CONFIG_NAME
```
If the config\_name is set to "default" or other invalid names, the default config will be shown.

To delete a config, use

```shell
$ kan del-config CONFIG_NAME
```

Besides, you can also assign a config to the default config using

```shell
$ kan set-default-config CONFIG_NAME
```

+ Kan

To kan (monitor) a job or task, just use

```shell
$ kan job PID & # for job running on shell, not recommended
$ kan tsk JOBID & # for task submitted to cluster, not recommended
```

Then `kan` will continue monitoring the job/task by is PID/JOBID until the job/task ends. After that, an email from the sender to the receiver, or a reminder via webhook according to your config will be sent.

**To prevent your kan process from being interrupted when the terminal exits, you can set the following statement in your `.bashrc` and then `source` it.**

```shell
alias kj="setsid kan job"
alias kt="setsid kan tsk"
```
Hence, just use:
```shell
$ kj PID
$ kt JOBID
```
Your kan process will continue to monitor the job/task and will not be affected by the exit of your terminal.

### Latest update: 0.4
A new subcommand `kan send` is now provided. You can straightly send messages to your configs (e.g. this command can be embeded into your `.sh` script etc.). Type `kan send --help` to see more.

