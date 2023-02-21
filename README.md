# benbb96

[![Deploy to PythonAnywhere](https://github.com/Benbb96/benbb96-website/actions/workflows/deploy-to-pythonanywhere.yml/badge.svg)](https://github.com/Benbb96/benbb96-website/actions/workflows/deploy-to-pythonanywhere.yml)
![GitHub repo size](https://img.shields.io/github/repo-size/benbb96/benbb96-website)
![GitHub contributors](https://img.shields.io/github/contributors/benbb96/benbb96-website)
![issues](https://img.shields.io/github/issues/benbb96/benbb96-website)
![GitHub stars](https://img.shields.io/github/stars/benbb96/benbb96-website?style=social)
![GitHub forks](https://img.shields.io/github/forks/benbb96/benbb96-website?style=social)
![Twitter Follow](https://img.shields.io/twitter/follow/benbb96?style=social)

This is my very personal Django project where I want to put all of my ideas to make my life easier.

### Why is it public ?

I'm always open to remarks and suggestions in order to progress in Python and Django !

## Installing benbb96

To install and use my website, follow these steps:

```
git clone https://github.com/Benbb96/benbb96-website.git
cd benbb96
```

Create a file here which will store all secrets settings : `secrets.json`.  
You can configure it like this :

```
{
  "SECRET_KEY": "[YOUR SECRET_KEY]",
  "GOOGLE_API_KEY": "[YOUR GOOGLE_API_KEY]",
  "GOOGLE_ANALYTICS_KEY": "[YOUR GOOGLE_ANALYTICS_KEY]",
  "FIREBASE_CONFIG": {
    [YOUR FIREBASE CONFIG]
  },
  "EMAIL_HOST_USER": "[YOUR EMAIL_HOST_USER]",
  "EMAIL_HOST_PASSWORD": "[YOUR EMAIL_HOST_PASSWORD]"
}
```

Then, you should create a virtual environement, load the migration to build the database (`db.sqlite3`), create a superuser to be able to access the administration module, and finally run the server :

```
python -m venv venv
source venv/bin/activate
pip install -r requirements/dev.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
python manage.py runserver
```

You can then create projects in [127.0.0.1:8000/admin/base/projet/](http://127.0.0.1:8000/admin/base/projet/) that will be displayed on the homepage.

## Contact 

If you want to contact me you can reach me at <benbb96@gmail.com>.

## License 

This project uses the following license: [MIT License](LICENSE).
