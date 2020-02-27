# Serverless Telegram Email Notification

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)

## About <a name = "about"></a>

This is a program that can notify you whenever there is a new email coming in (Long-polling), utilized serverless framework for saving costs.

The use-cases of this script is when you have a similar situation as below:

Not all members in the organisation have the access to the email, but you would like to get every member notified.

There are similar softwares / solutions but there will be more features coming up to suit more to the problem stated.

## Getting Started <a name = "getting_started"></a>

The step-by-step tutorial is still under development.

### Prerequisites

This program will require you to have an account on any Serverless Infrastructure Providers listed on <a href="https://serverless.com/framework/docs/providers/" target="_blank">serverless website</a>

If you do not have an account and you would like to host it on your local machine, you may check out <a href="https://github.com/pupubird/Python_telegram_email_notification" target="_blank">another repo</a>

A budget breakdown on using aws lambda function in 28-Feb-2020:

Setup:

- Polling at a period of 5 minutes using CloudWatch
- Memory limit of 256MB
- 20s timeout

Total USD per month = 0.20

### Installing

[Serverless Framework](https://serverless.com/) will be used to ease out the work of deployment

```bash
npm i -g serverless
```

As `requests` module is [removed](https://github.com/boto/botocore/pull/1829) from aws lambda, we will need to install it on the local folder as well

```bash
pip install requests -t .
```

The rest steps is still under development...
