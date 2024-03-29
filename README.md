# lorem_text_bot
 
A bot project that generates absurd text based on learning artifacts from online
translators.

### Basis

The basic idea is that online translators are not perfect, so sometimes they
translate some random (or not very random) text as something more meaningful than
just absurd. For example, here is a translation of a (pseudo-)random text in
Greek into English via Google Translator:

```
Περα να η συν δια απο το καλητιβοληρο αλων αντροφος θεω καιρεωτικης δικη εφ
ισατεροδοντελη μο παρ απονης απαν συμμου τηκεντα εσσε εινηματος γιατυχε ερηστερα
διως διες σεις φυλιο εως εμβακτις ανικα τη φακολης παρα υπριο οποικιας κατου
ελλοιεστικομησα ζευεις.

Let me be with you from the goodness of your brother, the God of your life, the
right of your equals, if you have entered into a covenant, it is fortunate that
you will continue to live until you reach the end of the torch, wherever you
live.
```

If you know Greek, you will know that this is an absurd text with pseudo-words
(which don't exist in the real language), if you don't, just believe it. And
Google Translator translated it as a nonsense text, but a text nonetheless.

### What can do

The bot has two features: a pseudotext generator and a translator.

Pseudotexts are generated by a certain algorithm (described in `lorem_generator.py`)
with real texts. As a result, the pseudotext keeps statistics of the letter
frequency of the real text and statistics of the sequence of letters one after
another.

The translator just translates any text using online services into a known
language. Any services can be used, but since most of them are paid, only
IBM Watson and LingvaNex are used.

All bot commands use these features, combining them in some way.

Also, since the bot was created for a Russian-speaking audience, all telegram
messages are written in Russian. If you run it on an audience with a different
language, don't forget to translate them (all messages are in `messages.py`).

The logic of this project is a bit beyond translation:
- the bot has a second reduced version: this version provides fewer features and 
    only faster commands
- the bot tracks the posts of a given channel and knows how to forward random
    posts from there

If you want (most likely, yes) to use only the original translator bot, you can
use the parameter (in `.envs`) `"DEBUG"=True` and put a token in the
`"TOKEN_TEST"` parameter.

### Running

The required version of Python to run the bot is `3.8+`.

You can run it locally or on a hosting server. Commands to get a project on the
machine:

```shell
git clone https://github.com/tetelevm/lorem_text_bot
cd ./lorem_text_bot
python3 -m venv env
. ./env/bin/activate
python3 install -r requirements.txt
```

Next you need to configure the environment:
- create a file `.envs` following the example of file `.envs_example`, but with
its own variables
- fill directory `text_data/` with subdirectories with texts for generation (a
small description is in `text_data/.gitkeep`)
- add a file `chinese.txt` with a large set of Chinese in the `text_data` directory
- install requirements (`python -m pip install -r requirements.txt`)

And after that you can start the project. To run locally (running temporarily,
e.g. for development) just execute `python3 main.py`.

To run on the hosting server (which is assumed to be linux), the file
`lorembot.service` is created. It must be copied to `/lib/systemd/system/` (don't
forget to check and correct the paths) and run two commands:

```shell
systemctl enable lorembot.service
systemctl start lorembot.service
```

### If anything

If you have any questions/ideas, the `Issues` section is available!
