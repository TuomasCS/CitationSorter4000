# OKD deployment

## Requirements

You need:

- Access to the [University VPN](https://helpdesk.it.helsinki.fi/ohjeet/kirjautuminen-ja-yhteydet/verkkoyhteydet/eduvpn-helsingin-yliopistolla)

- Install the `oc` command-line tool and log in to OKD by following the [course OKD instructions on GitHub](https://github.com/ohjelmistotuotanto-hy/miniprojekti-boilerplate/blob/main/OKD.md).

- Create a local `secret.env` file from the template:

```bash
cp secret.env.template secret.env 
```

Generate a random secret key:

```bash
SECRET_KEY=$(openssl rand -hex 32)
printf 'SECRET_KEY=%s\n' "$SECRET_KEY" > secret.env
```
Replace changeme to generated key in secret.inv

## Manual deployment

Normal code changes are deployed automatically after pushing to `main`.

Run this command only after changing deployment settings:

```bash
oc apply -k .
```

More information is available in the
[course deployment instructions](https://github.com/ohjelmistotuotanto-hy/miniprojekti-boilerplate/blob/main/DEPLOYMENT.md).