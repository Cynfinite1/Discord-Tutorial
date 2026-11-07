"""Builds every page of the Discord for School tutorial.
Run: python3 build.py

Each section and each subsection is its own page. The left sidebar
(Table of Contents) is generated from SECTIONS so it is identical on every page.
New words use T('key') and show their definition on hover or keyboard focus.
Media placeholders use media('note for Sebastian') and render as blank boxes.
"""
import html, os, re, glob

SITE = 'Discord for School'
TITLE = "Discord for College: Desktop App Version"

# ---------------------------------------------------------------------------
# New words (blue text + hover definition). Also used to build the Glossary.
# ---------------------------------------------------------------------------
DEF = {
    'desktop app': 'The version of Discord you download and install on a Windows PC.',
    'server': 'A private space on Discord for one group, class, or club. Each server has its own channels and members.',
    'channel': 'A separate area inside a server for one topic or activity. A server can have many channels.',
    'text channel': 'A channel marked with a pound sign (#) where people type messages and share files.',
    'voice channel': 'A channel marked with a speaker icon where people talk live with their voice, camera, or screen.',
    'username': 'Your unique account name. No two Discord accounts can have the same username.',
    'display name': 'The name other people see next to your messages. It does not have to be unique.',
    'CAPTCHA': 'A short puzzle, such as a checkbox or picture question, that proves you are a person and not a program.',
    'avatar': 'Your profile picture. It appears next to every message you send.',
    'User Settings': 'The menu where you change your account, profile, language, and text size. Open it with the gear icon at the bottom left.',
    'invite link': 'A web address, usually starting with discord.gg/, that lets you join a specific server.',
    'server nickname': 'A name you use in only one server. It replaces your display name in that server and nowhere else.',
    'member list': 'The column on the right side of a server that shows who belongs to the server and who is online.',
    'server list': 'The column of round icons on the far left of Discord. Each icon is a server you belong to.',
    'channel list': 'The column next to the server list that shows every channel in the server you selected.',
    'chat area': 'The large center area of Discord that shows the messages in the channel you selected.',
    'user panel': 'The small bar at the bottom left of Discord with your name, your microphone button, your headphone button, and the gear icon.',
    'mute': 'To turn off your microphone so no one can hear you. You can still hear others.',
    'deafen': 'To turn off all sound coming into Discord. Deafening also mutes your microphone.',
    'category': 'A heading in the channel list that groups related channels, such as TEXT CHANNELS or VOICE CHANNELS.',
    'reply': 'A message that is attached to an earlier message so everyone can see what you are answering.',
    'reaction': 'A small emoji added under a message. Groups often use reactions to say "I saw this" or to vote.',
    'direct message': 'A private conversation between you and one person or a small group, outside of any server. Often shortened to DM.',
    'thread': 'A side conversation attached to one message in a channel, so a long discussion does not crowd the main channel.',
    'mention': 'Typing the @ symbol followed by a name so that person receives a notification. Also called a ping.',
    'role': 'A label a server gives to a group of members, such as @Presenters. Roles can control who sees certain channels.',
    'moderator': 'A server member who manages channels, roles, and members, and keeps the server organized.',
    'unread indicator': 'A white dot or bold channel name that shows there are new messages you have not read.',
    'mention badge': 'A red circle with a number that shows how many times someone mentioned you.',
    'Inbox': 'The tray icon at the top right of Discord that collects your recent mentions and unread messages in one list.',
    'pinned message': 'An important message that a group saves to a channel\'s pinned list so it is easy to find later.',
    'attachment': 'A file, such as a document, slide deck, or image, that you add to a message.',
}

ICON = {
    'note': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>',
    'caution': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>',
    'menu': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18"/></svg>',
}

LOGO = '<img src="media/discord-logo.png" alt="" width="36" height="36">'


def T(key, shown=None):
    """A new word: blue text, definition on hover/focus."""
    d = html.escape(DEF[key], quote=True)
    return f'<span class="term" tabindex="0" data-def="{d}">{shown or key}</span>'


def note(h):
    return (f'<aside class="callout note" role="note" aria-label="Note">{ICON["note"]}'
            f'<p><span class="label">Note</span>{h}</p></aside>')


def caution(h):
    return (f'<aside class="callout caution" role="note" aria-label="Caution">{ICON["caution"]}'
            f'<p><span class="label">Caution</span>{h}</p></aside>')


def media(todo, small=False):
    """Marks a media spot. Each marker is numbered by page and position (for example 2.3.1)
    when the page is written. A matching file in media/ is shown; otherwise a placeholder."""
    return f'@@MEDIA[{html.escape(todo, quote=True)}]@@'


# Alt text for media that is ready, keyed by label (subsection number + position)
MEDIA = {
    '1.3.4': 'This tutorial open in a web browser on the left half of the screen and Discord open on the right half',
    '2.1.2': 'The Discord download page with the Download for Windows button',
    '2.2.2': 'Accessing the create an account form after clicking register on the login screen',
    '2.2.10': 'The Discord home screen after signing up, with a green bar at the top asking you to verify your email',
    '2.2.13': 'Opening the verification email and clicking Verify Email',
    '2.3.2': 'The user panel at the bottom left, with the gear icon to the right of the microphone and headphone buttons',
    '2.3.16': 'The Text size in chat slider under Text Readability in the Accessibility settings',
}


def render_media(label, todo, section):
    for ext in ('webp', 'png', 'gif', 'jpg'):
        if os.path.exists(f'media/{label}.{ext}'):
            alt = html.escape(MEDIA.get(label, todo), quote=True)
            return (f'<figure class="media"><a class="media-frame" href="media/{label}.{ext}" target="_blank" rel="noopener" '
                    f'aria-label="Open {label} full size"><img src="media/{label}.{ext}" alt="{alt}" loading="lazy" decoding="async"></a>'
                    f'<figcaption>Figure {label}: {alt}</figcaption></figure>')
    if os.path.exists(f'media/{label}.mp4'):
        alt = html.escape(MEDIA.get(label, todo), quote=True)
        return (f'<figure class="media"><div class="media-frame"><video controls preload="metadata" playsinline '
                f'poster="media/{label}-poster.jpg" aria-label="{alt}"><source src="media/{label}.mp4" type="video/mp4"></video>'
                f'<a class="open-new" href="media/{label}.mp4" target="_blank" rel="noopener">Open video in a new window</a></div>'
                f'<figcaption>Figure {label}: {alt}</figcaption></figure>')
    note = f'<!-- MEDIA PLACEHOLDER {label}: {todo}. Save your file as media/{label}.png, .gif, or .mp4. -->'
    return note + f'<figure class="media placeholder"><p class="placeholder-text">Image, Gif or Video will go here</p><figcaption>Figure {label}</figcaption></figure>'


def number_media(body, num):
    count = [0]
    def rep(m):
        count[0] += 1
        return render_media(f'{num}.{count[0]}', html.unescape(m.group(1)), num.split('.')[0])
    return re.sub(r'@@MEDIA\[(.*?)\]@@', rep, body)


def steps(*items):
    """Numbered steps. Every step gets its own media spot: step text on the left, media on the right."""
    out = []
    for it in items:
        text = it[0] if isinstance(it, tuple) else it
        todo = re.sub(r'<[^>]+>', '', text)
        out.append(f'<li><div class="step-text">{text}</div><div class="step-media">{media("Step: " + todo)}</div></li>')
    return '<ol class="steps steps-grid">' + ''.join(out) + '</ol>'


def explain():
    """Spot for a short paragraph that explains a figure before it is shown (to be written by Sebastian)."""
    return '<p class="placeholder-text explain">Explanatory paragraph will go here</p>'


def result(h):
    return f'<p class="result"><strong>Result:</strong> {h}</p>'


def ui(label):
    return f'<strong class="ui">{label}</strong>'


def kbd(k):
    return f'<kbd>{k}</kbd>'


# ---------------------------------------------------------------------------
# Site structure. Each entry: (number, file, title, summary, [subsections])
# Subsection: (number, file, title, summary)
# ---------------------------------------------------------------------------
SECTIONS = [
    ('1', 'index.html', 'Introduction: What Discord Is and Why Your Group Uses It', 'What Discord is and why classes and clubs use it.', [
        ('1.1', 'about-this-tutorial.html', 'About This Tutorial', 'What you will be able to do and what you need before you begin.'),
        ('1.2', 'who-this-is-for.html', 'Who This Tutorial Is For', 'The skills, equipment, and time you need before you start.'),
        ('1.3', 'how-to-use.html', 'How to Use This Tutorial', 'How the pages, steps, notes, and new words work.'),
    ]),
    ('2', 'getting-started.html', 'Getting Started: Creating Your Account', 'Install Discord on your computer and create your account.', [
        ('2.1', 'download-app.html', 'Downloading the Desktop App', 'Install Discord on a Windows PC.'),
        ('2.2', 'sign-up.html', 'Signing Up and Verifying Your Email', 'Register, choose your names, and confirm your email address.'),
        ('2.3', 'profile-settings.html', 'Setting Up Your Profile and Comfort Settings', 'Add an avatar and pronouns, change the language, and make text larger.'),
    ]),
    ('3', 'joining-a-server.html', 'Joining Your Class or Group Server', 'Join the server your group invited you to and set your name there.', [
        ('3.1', 'what-is-a-server.html', 'What a Server Is', 'How servers, channels, and members fit together.'),
        ('3.2', 'accept-invite.html', 'Accepting an Invite Link', 'Join from a link, or paste the link into Discord.'),
        ('3.3', 'server-nickname.html', 'Setting a Server Nickname', 'Use your full name in one server only.'),
    ]),
    ('4', 'discord-layout.html', 'Understanding the Discord Layout', 'A guided tour of the Discord window from left to right.', [
        ('4.1', 'four-areas.html', 'The Four Main Areas of the Screen', 'The server list, channel list, chat area, and member list.'),
        ('4.2', 'channels.html', 'Text Channels and Voice Channels', 'Tell the two kinds of channels apart by their icons.'),
        ('4.3', 'user-panel.html', 'Your User Panel', 'The microphone, headphone, and settings buttons.'),
    ]),
    ('5', 'communicating.html', 'Communicating with Your Group', 'Send messages, use mentions, catch up, and share files.', [
        ('5.1', 'messages.html', 'Sending Messages and Direct Messages', 'Type, edit, reply, react, message privately, and use threads.'),
        ('5.2', 'mentions.html', 'Using Mentions', 'Notify one teammate, a role, or the whole server.'),
        ('5.3', 'missed-messages.html', 'Finding Messages You Missed', 'Unread indicators, the Inbox, pinned messages, and search.'),
        ('5.4', 'files.html', 'Sharing and Finding Files', 'Upload documents and find them again later.'),
    ]),
    ('6', 'notifications-privacy.html', 'Managing Notifications and Privacy', 'Control alerts and protect your account.', [
        ('6.1', 'notifications.html', 'Controlling Notifications', 'Keep important alerts and silence the rest.'),
        ('6.2', 'privacy-security.html', 'Protecting Your Privacy and Account', 'Limit who can contact you and secure your login.'),
    ]),
    ('7', 'voice-and-screen.html', 'Joining Voice Calls and Sharing Your Screen', 'Attend group meetings and present your work.', [
        ('7.1', 'voice-video.html', 'Joining a Voice Channel and Turning On Video', 'Connect, mute, disconnect, and use your camera.'),
        ('7.2', 'screen-share.html', 'Sharing Your Screen', 'Present one window or your entire screen.'),
        ('7.3', 'meeting-etiquette.html', 'Meeting Etiquette for Group Projects', 'Habits that keep group calls smooth.'),
    ]),
    ('8', 'conclusion.html', 'Conclusion and Next Steps', 'Review what you learned and keep going.', [
        ('8.1', 'checklist.html', 'Quick-Start Checklist', 'The core skills in one list.'),
        ('8.2', 'beyond.html', 'Beyond Your Group Project', 'Using Discord for clubs and future classes.'),
    ]),
    ('9', 'troubleshooting.html', 'Troubleshooting Common Problems', 'Fixes organized by problem.', [
        ('9.1', 'audio-video-problems.html', 'Audio and Video Problems', 'Fix microphone, speaker, and camera problems.'),
        ('9.2', 'channel-invite-problems.html', 'Channel and Invite Problems', 'Fix missing channels and expired invites.'),
        ('9.3', 'getting-help.html', 'Getting More Help', 'Ask your server for help the right way.'),
    ]),
    ('10', 'glossary.html', 'Glossary', 'Every new word in this tutorial, defined in plain language.', []),
]

# Flat reading order for previous / next links
ORDER = []
for num, f, title, summ, subs in SECTIONS:
    ORDER.append((num, f, title, None))
    for snum, sf, stitle, ssumm in subs:
        ORDER.append((snum, sf, stitle, (num, f, title)))


def sidebar(current):
    out = []
    for num, f, title, summ, subs in SECTIONS:
        cur = ' aria-current="page"' if f == current else ''
        out.append(f'<li><a class="sec" href="{f}"{cur}><span class="n">{num}.</span> {title}</a>')
        if subs:
            out.append('<ul>')
            for snum, sf, stitle, ssumm in subs:
                scur = ' aria-current="page"' if sf == current else ''
                out.append(f'<li><a class="sub" href="{sf}"{scur}><span class="n">{snum}</span> {stitle}</a></li>')
            out.append('</ul>')
        out.append('</li>')
    return '<ul class="toc-list">' + ''.join(out) + '</ul>'


def page(filename, body, description, draft=False):
    idx = next(i for i, o in enumerate(ORDER) if o[1] == filename)
    num, _, title, parent = ORDER[idx]
    prev = ORDER[idx - 1] if idx > 0 else None
    nxt = ORDER[idx + 1] if idx + 1 < len(ORDER) else None
    crumbs = '<a href="index.html">Home</a>'
    if parent:
        crumbs += f' <span aria-hidden="true">/</span> <a href="{parent[1]}">Section {parent[0]}</a>'
        crumbs += f' <span aria-hidden="true">/</span> <span aria-current="page">{num}</span>'
    elif filename != 'index.html':
        crumbs += f' <span aria-hidden="true">/</span> <span aria-current="page">Section {num}</span>'
    label = f'Section {num}' if parent is None else f'Subsection {num}'
    pager = '<nav class="pager" aria-label="Previous and next pages">'
    if prev:
        pager += f'<a class="prev" href="{prev[1]}"><small>Previous</small><span>{prev[0]} {prev[2]}</span></a>'
    else:
        pager += '<span></span>'
    if nxt:
        pager += f'<a class="next" href="{nxt[1]}"><small>Next</small><span>{nxt[0]} {nxt[2]}</span></a>'
    pager += '</nav>'
    draft_banner = (f'<p class="draft">This {"section" if parent is None else "subsection"} is unfinished.</p>'
                    if draft else '')
    heading = f'{num}. {title}' if parent is None else f'{num} {title}'
    doc_title = f'{heading} | {TITLE}' if filename != 'index.html' else TITLE
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{doc_title}</title>
<meta name="description" content="{html.escape(description, quote=True)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;600;700;800&display=swap" rel="stylesheet">
<link rel="icon" type="image/png" href="favicon.png">
<link rel="stylesheet" href="styles.css">
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<div class="shell">
  <aside class="sidebar" id="sidebar" aria-label="Table of Contents">
    <a class="brand" href="index.html"><span class="brand-mark">{LOGO}</span><span>{TITLE}</span></a>
    <h2 class="toc-title">Table of Contents</h2>
    <nav aria-label="Table of Contents">{sidebar(filename)}</nav>
  </aside>
  <div class="main-col">
    <header class="topbar">
      <button class="toc-toggle" aria-expanded="false" aria-controls="sidebar">{ICON['menu']}<span>Table of Contents</span></button>
      <span class="topbar-title">{TITLE}</span>
    </header>
    <main id="main" class="content">
      <nav class="crumbs" aria-label="Breadcrumb">{crumbs}</nav>
      {f'<h1>{TITLE}</h1><p class="section-label">{heading}</p>' if filename == 'index.html' else f'<h1>{heading}</h1>'}
      {draft_banner}
{body}
{pager}
    </main>
  </div>
</div>
<div class="term-tip" id="term-tip" role="tooltip" hidden></div>
<script src="script.js"></script>
</body>
</html>
'''


def overview(num):
    """Pathway list of links + short descriptions for a section page."""
    sec = next(s for s in SECTIONS if s[0] == num)
    items = ''.join(f'<li><a href="{sf}"><span class="n">{snum}</span> {st}</a><p>{ss}</p></li>' for snum, sf, st, ss in sec[4])
    return f'<ul class="pathway">{items}</ul>'


PAGES = {}

# ===========================================================================
# SECTION 1  INTRODUCTION (homepage: What Discord Is)
# ===========================================================================
PAGES['index.html'] = ('Learn what Discord is and why your class or group uses it, then learn the Discord desktop app one short section at a time.', f'''
<p class="lead"><a href="https://discord.com">Discord</a> is a free app that keeps a group's messages, files, and meetings in one place. This page explains how Discord is organized and why your group chose it.</p>

<h2>What Discord does</h2>
<p>Discord combines three tools that groups usually keep separate:</p>
<ul>
  <li><strong>Typed chat</strong> for questions, updates, and links</li>
  <li><strong>Voice and video calls</strong> for meetings</li>
  <li><strong>File sharing</strong> for drafts, slides, and images</li>
</ul>
<p>Each group gets its own {T('server')}. Inside the server, conversations are split into {T('channel', 'channels')}, and each channel has one topic, such as announcements or file drafts. Because topics stay separate, you can go straight to the information you need instead of scrolling through one long chat.</p>

<h2>Why classes and clubs choose Discord</h2>
<p>Many UCF project groups and student organizations use Discord for four reasons:</p>
<ul>
  <li><strong>It is free:</strong> Every feature in this tutorial works without a paid plan.</li>
  <li><strong>It is organized by topic:</strong> Announcements, files, and casual chat each have their own channel.</li>
  <li><strong>Meetings need no link:</strong> A meeting room stays open, so members join with one click instead of waiting for a new meeting link.</li>
  <li><strong>It works on every device:</strong> The desktop app, the browser version, and the phone app all show the same messages.</li>
</ul>

{note('Discord is also popular for gaming, but you do not need any gaming experience. A school server only contains the channels your group creates.')}

<h2>Start here</h2>
<p>Read the three parts of this introduction first, or go straight to <a href="getting-started.html">Section 2: Creating Your Account</a> if you are ready to install Discord.</p>
{overview('1')}
''')

PAGES['about-this-tutorial.html'] = ('What this tutorial teaches and what you need before you begin.', f'''
<p class="lead">Your group says everything is on Discord, but you are not sure where to look. This tutorial will teach you how to use the Discord {T('desktop app')} for a class or group project, from creating your account to joining your group's meetings.</p>

<p>You can use Discord on a computer, in a web browser, or on a phone. This tutorial covers <strong>only the desktop app for Windows</strong>, so every step and every picture matches what you see on your computer screen.</p>

<h2>What you will be able to do</h2>
<ul>
  <li>Create an account and set up a profile your teammates recognize</li>
  <li>Join your group's server and find the right channels</li>
  <li>Send messages, reply, and share files</li>
  <li>Find deadlines and meeting changes you missed</li>
  <li>Join voice meetings and share your screen</li>
</ul>

<h2>Before you begin</h2>
<table class="facts">
  <tr><th scope="row">Skill level</th><td>You only need to be comfortable with email, a web browser and messaging apps.</td></tr>
  <tr><th scope="row">You need</th><td>A Windows 10 or 11 PC, an internet connection, and an email address you can access</td></tr>
  <tr><th scope="row">Voice/Video Calls</th><td>A microphone and speakers or headphones. A webcam is optional.</td></tr>
</table>

''')

PAGES['who-this-is-for.html'] = ('The audience, skills, equipment, and time this tutorial expects.', f'''
<p class="lead">This tutorial is for students who have never used Discord and need it for a class, group project, or student organization.</p>

<h2>Who will get the most from this tutorial</h2>
<p>You will get the most from this tutorial if you:</p>
<ul>
  <li>Already use email, Canvas, any messaging app such as WhatsApp, and Zoom</li>
  <li>Have a group that asked you to join their Discord server</li>
  <li>Want to keep up with messages without spending hours learning a new app</li>
</ul>

<h2>What you need before you start</h2>
<ul>
  <li>A Windows 10 or 11 PC</li>
  <li>An internet connection</li>
  <li>An email address you can check right away, such as your Knights email</li>
  <li>A microphone and speakers or headphones for voice and video calls</li>
</ul>

{caution('Library and work computers often block new programs from being installed. Use your own computer for this tutorial so you can install the desktop app.')}

<h2>What you do not need to know</h2>
<p>You do not need to know any Discord words before you begin. Every new word appears in <span class="term-sample">blue</span> text the first time it is used on a page. Point to the blue word with your mouse to read its definition. All new words are also collected in the <a href="glossary.html">Glossary</a>.</p>
''')

PAGES['how-to-use.html'] = ('How the pages, numbered steps, notes, cautions, and new words in this tutorial work.', f'''
<p class="lead">This tutorial is divided into short sections. Each section has its own page, and each topic inside a section has its own page, so you can stop and return at any time.</p>

<h2>Navigation</h2>
<p>Each section builds on the one before it. Use the <strong>Table of Contents</strong> on the left to jump to any page, or use the <strong>Next</strong> button at the bottom of each page to keep reading in order.</p>

<h2>Keep the tutorial and Discord side by side</h2>
<p>Open this tutorial in your web browser on one half of your screen and the Discord app on the other half. You can then read a step and complete it without switching windows.</p>
{steps(
    'Open this tutorial in your web browser.',
    f'Press {kbd("Windows key")} + {kbd("Left Arrow")} to move the browser to the left half of the screen.',
    'Open the Discord app.',
    f'Press {kbd("Windows key")} + {kbd("Right Arrow")} to move Discord to the right half of the screen.',
)}

<h2>How each page is written</h2>
<ul>
  <li><strong>Numbered steps</strong> tell you one action at a time. Complete them in order.</li>
  <li><strong>Bold words</strong> such as {ui('Continue')} match the buttons and menu names on your screen.</li>
  <li><strong>Pictures</strong> appear next to each step they show.</li>
  <li><strong>Blue words</strong>, such as {T('server')}, are new words. Point to them to see the definition.</li>
</ul>

<h2>Notes, cautions, and results</h2>
<p>Three kinds of boxes set off extra information:</p>
{note('A Note gives extra information that helps you complete a task.')}
{caution('A Caution warns you about something that could cause a problem with your account or your work.')}
{result('A Result appears after a set of steps and tells you what you should see when you finish them correctly. If your screen does not match, go back and check each step.')}
''')

# ===========================================================================
# SECTION 2  GETTING STARTED
# ===========================================================================
PAGES['getting-started.html'] = ('Install the Discord desktop app and create your account.', f'''
<p class="lead">In this section, you will install the {T('desktop app')}, create your account, and set up a profile your teammates recognize.</p>
<p><strong>You need:</strong> your computer and an email address you can check.</p>
{overview('2')}
''')

PAGES['download-app.html'] = ('Download and install the Discord desktop app on Windows.', f'''
<p class="lead">The {T('desktop app')} is the most complete version of Discord and the version this tutorial uses. Installing it takes about five minutes.</p>

<h2>Install Discord on Windows</h2>
{steps(
    'Open your web browser and go to <strong>discord.com/download</strong>.',
    (f'Click {ui("Download for Windows")}.', media('Your screenshot of the download page with the Download for Windows button circled', True)),
    f'Open the file <strong>DiscordSetup.exe</strong> from your Downloads folder.',
    'Wait while Discord installs. The app opens on its own when it finishes.',
)}
{result('The Discord login screen appears, and a Discord shortcut is added to your Start menu.')}

{caution('Download Discord only from discord.com. Copies offered on other websites can contain harmful software.')}
''')

PAGES['sign-up.html'] = ('Register for a Discord account, choose your names, and verify your email.', f'''
<p class="lead">Creating your account takes about five minutes. You will choose two names, so read the short explanation below before you start.</p>

<h2>Choosing a username and display name</h2>
<p>Discord asks you for two different names:</p>
<ul>
  <li>Your {T('username')} is unique, like an email address. It can use only lowercase letters, numbers, periods, and underscores.</li>
  <li>Your {T('display name')} is the name teammates see next to your messages. It can include spaces and capital letters.</li>
</ul>
<p>For school, use a display name your classmates and instructors recognize, such as your first and last name. You can still change it later.</p>

<h2>Sign up</h2>
{steps(
    'Open the Discord app.',
    (f'On the login screen, click {ui("Register")} under the {ui("Log In")} button.', media('Your screenshot of the login screen with Register circled', True)),
    'Type your email address.',
    'Type your display name.',
    'Type a username. If the name is taken, Discord asks you to choose another one.',
    'Type a password that you do not use for any other account.',
    'Select your month, day, and year of birth.',
    f'Click {ui("Continue")}.',
    f'Complete the {T("CAPTCHA")} puzzle, such as checking the box next to <strong>I am human</strong>.',
)}
{result('Discord opens to your home screen, and a verification email is sent to your inbox.')}
<p>Congratulations! Your Discord is installed and logged in, yours should appear as shown below.</p>
{media('Home screen after signing up')}

<h2>Verify your email address</h2>
<p>Discord will not let you join some servers until you verify your email address.</p>
{steps(
    'Open your email inbox.',
    'Open the email from Discord with the subject <strong>Verify Email Address for Discord</strong>.',
    (f'Click {ui("Verify Email")}.', media('Your screenshot of the verification email with the Verify Email button circled', True)),
)}
{result('A web page opens that says your email is verified. You can close that browser tab and return to the app.')}

{note('If the email does not arrive within five minutes, check your spam or junk folder. You can also click <strong>Resend</strong> on the green bar at the top of the Discord app.')}
''')

PAGES['profile-settings.html'] = ('Add an avatar and pronouns, switch Discord to Spanish or another language, and make text larger.', f'''
<p class="lead">An avatar and pronouns help your group recognize you, and comfort settings make Discord easier to read. All three tasks on this page start in {T('User Settings')}.</p>

<h2>Open User Settings</h2>
{steps(
    'Find your name at the bottom-left corner of the Discord window.',
    (f'Click the gear icon to the right of your name.', media('Your screenshot of the bottom-left corner with the gear icon circled', True)),
)}
{result('The User Settings menu opens, with a list of options on the left. Press <kbd>Esc</kbd> at any time to close it.')}

<h2>Adding an Avatar and Pronouns</h2>
<p>Your {T('avatar')} appears next to every message you send. A clear photo of your face or a simple image helps teammates match your messages to you. Adding your pronouns helps teammates know how to refer to you.</p>
{steps(
    f'In User Settings, click {ui("Edit Profiles")}.',
    f'Click on your {ui("Avatar")}, and then click the {ui("Change Avatar")} button.',
    f'Click {ui("Upload Image")}.',
    'Choose a picture from your computer.',
    'Drag the picture or use the buttons below to adjust the crop.',
    f'Click {ui("Apply")}.',
    f'Click {ui("Save Changes")} at the bottom of the window.',
    f'Click the area that says {ui("Add pronouns")}, next to your username.',
    'Type your preferred pronouns, such as <strong>He/Him</strong>.',
    f'Click {ui("Save Changes")}.',
)}
{result('Your new picture appears in the bottom-left corner next to your name, and your pronouns appear on your profile card.')}

<h2>Change the display language</h2>
<p>You can switch every menu and button in Discord to another language, such as Spanish. Messages from your group stay in the language they were written in.</p>
{steps(
    f'In User Settings, scroll down and click {ui("Language & Time")}.',
    f'Click the language you want, such as {ui("Español, LATAM")}.',
)}
{result('Discord changes language right away. No restart is needed.')}
{note('This tutorial uses the English names of buttons. If you change the language, switch it back to English while you work through the steps, or keep this tutorial open beside Discord to match the button positions.')}

<h2>Make text larger</h2>
{steps(
    f'In User Settings, click {ui("Accessibility")}.',
    f'Under {ui("Text Readability")}, find {ui("Text size in chat")}.',
    'Drag the slider to the right until messages are comfortable to read.',
)}
{result('Messages in every channel use the larger size.')}
{note(f'To make everything in Discord larger, including menus, press {kbd("Ctrl")} + {kbd("+")}. Press {kbd("Ctrl")} + {kbd("0")} to return to normal size.')}
''')

# ===========================================================================
# SECTION 3  JOINING A SERVER
# ===========================================================================
PAGES['joining-a-server.html'] = ('Join your class or group server from an invite link and set your name there.', f'''
<p class="lead">Joining your group's {T('server')} is usually the first thing a group asks a new member to do. This section explains what a server is, shows you how to join one, and shows you how to set your name for that server.</p>
<p><strong>You need:</strong> the invite link your group sent you.</p>
{overview('3')}
''')

PAGES['what-is-a-server.html'] = ('What a Discord server is and how one account can belong to many servers.', f'''
<p class="lead">A {T('server')} is a private space for one group, class, or club. Only people who are invited can join it.</p>

<h2>What is inside a server</h2>
<p>Every server contains the same basic parts:</p>
<ul>
  <li><strong>Members:</strong> the people who joined the server</li>
  <li>{T('channel', '<strong>Channels</strong>')}<strong>:</strong> separate areas for each topic, such as #announcements or #files-and-drafts</li>
  <li><strong>Owner and moderators:</strong> the people who set up the channels and manage the server, such as a group leader or club officer</li>
</ul>
{media('Your screenshot of a sample group project server with its channels and members visible')}

<h2>One account, many servers</h2>
<p>You only need one Discord account, even if you join servers for several classes and clubs. Each server you join appears as a round icon in the column on the far left of the Discord window. Click an icon to switch to that server.</p>
{media('Your screenshot of the server icons on the far left with several school servers', True)}

{note('Leaving a server does not delete your account. You can rejoin later if someone sends you a new invite link.')}
''')

PAGES['accept-invite.html'] = ('Join a Discord server from an invite link on your computer.', f'''
<p class="lead">Groups invite new members by sending an {T('invite link')}, usually by email, text message, or a Canvas message. The link looks like <strong>discord.gg/</strong> followed by a short code.</p>

<h2>Join by clicking the link</h2>
{steps(
    'Make sure you are logged in to the Discord desktop app.',
    f'Click the {ui("Join")} button on the invite link your group sent.',
)}
{result('Discord opens to the new server, and its icon appears in the column on the far left.')}

<h2>Join by pasting the link</h2>
<p>If clicking the link does not open the server, paste the link into Discord yourself.</p>
{steps(
    'Copy the invite link from the email or message.',
    (f'In Discord, click the plus button ({ui("Add a Server")}) near the bottom of the round server icons on the far left.', media('Your screenshot of the plus button circled in the server list', True)),
    f'At the bottom of the window that opens, click {ui("Join a Server")}.',
    f'Paste the link into the {ui("Invite Link")} box.',
    f'Click {ui("Join Server")}.',
)}
{result('The new server opens, and its icon appears in the server column.')}

{caution('If Discord says the invite is invalid or expired, ask your group for a new link. Invite links can be set to stop working after a certain time or number of uses.')}
''')

PAGES['server-nickname.html'] = ('Set a server nickname so you use your full name in one server only.', f'''
<p class="lead">A {T('server nickname')} changes your name in one server without changing it anywhere else. Use your full name in class servers so teammates and instructors know who wrote each message.</p>

<h2>Set your server nickname</h2>
{steps(
    'Click your profile in the member list.',
    f'Click {ui("Edit Profile")}, and then click {ui("Edit Per-server Profile")}.',
    f'Type your nickname in the {ui("Display Name")} box.',
    f'Click {ui("Save Changes")}.',
)}
{result('Your new nickname appears next to your messages in this server. Your name in all other servers stays the same.')}

{note('Some servers do not allow members to change their own nickname. If you do not see the option, ask a server moderator to set it for you.')}
''')

# ===========================================================================
# SECTION 4  LAYOUT
# ===========================================================================
PAGES['discord-layout.html'] = ('A guided tour of the Discord desktop window from left to right.', f'''
<p class="lead">A crowded screen is the most common reason beginners feel lost in Discord. This section walks through the window from left to right so you always know where to look.</p>
<p><strong>You need:</strong> Discord open to your group's server.</p>
{overview('4')}
''')

PAGES['four-areas.html'] = ('The server list, channel list, chat area, and member list in the Discord desktop app.', f'''
<p class="lead">The Discord window is divided into four main areas. Read them from left to right.</p>

<h2>1. Server list</h2>
<p>The {T('server list')} is the narrow column of round icons on the far left. Each icon is a server you belong to. The Discord logo at the top opens your private messages, which <a href="messages.html">Subsection 5.1</a> explains.</p>
{media('Server list')}

<h2>2. Channel list</h2>
<p>The {T('channel list')} shows every channel in the server you selected. The server name appears at the top. Channels are grouped under headings called {T('category', 'categories')}.</p>
{media('Channel list')}

<h2>3. Chat area</h2>
<p>The {T('chat area')} in the center shows the messages in the channel you selected. The newest messages are at the bottom, and the box for typing your own message is below them.</p>
{media('Chat area')}

<h2>4. Member list</h2>
<p>The {T('member list')} on the right shows who belongs to the server. Members who are online appear at the top.</p>
{media('Member list')}
{note('If you do not see the member list, click the icon of two people at the top-right of the window to show or hide it.')}
''')

PAGES['channels.html'] = ('How to tell text channels and voice channels apart in Discord.', f'''
<p class="lead">Every server has two main kinds of channels. You can tell them apart by the icon in front of each channel name.</p>

<h2>Text channels</h2>
<p>A {T('text channel')} has a pound sign (<strong>#</strong>) in front of its name, such as <strong>#announcements</strong>. Text channels are for typed messages, links, and files. Click a text channel to read it.</p>
{media('Text channels with the # icon')}

<h2>Voice channels</h2>
<p>A {T('voice channel')} has a speaker icon in front of its name, such as <strong>Meeting Room</strong>. Voice channels are for live talking, video, and screen sharing.</p>
{media('Voice channels with the speaker icon')}
{caution('Clicking a voice channel connects you to it immediately, and the other people in it may hear your microphone. Click a voice channel only when you are ready to talk.')}

<h2>Bold and gray channel names</h2>
<p>A channel name in <strong>bold white</strong> has messages you have not read. A gray channel name means you are caught up. <a href="missed-messages.html">Subsection 5.3</a> explains more ways to catch up.</p>
''')

PAGES['user-panel.html'] = ('The microphone, headphone, and settings buttons in the Discord user panel.', f'''
<p class="lead">The {T('user panel')} sits at the bottom of the channel list. It shows your picture and name and three buttons that control your sound and settings.</p>
{media('Close-up screenshot of the user panel with the three buttons labeled')}

<h2>The three buttons</h2>
<table class="facts">
  <tr><th scope="col">Button</th><th scope="col">What it does</th></tr>
  <tr><td><strong>Microphone</strong></td><td>Click it to {T('mute')} or unmute your microphone. A red line through the icon means you are muted.</td></tr>
  <tr><td><strong>Headphones</strong></td><td>Click it to {T('deafen')} or undeafen yourself. A red line through the icon means you hear no sound.</td></tr>
  <tr><td><strong>Gear</strong></td><td>Opens {T('User Settings')}, where you change your profile, language, and text size.</td></tr>
</table>

<h2>Muting compared with deafening</h2>
<p>Muting turns off only your microphone, so you can still hear your group. Deafening turns off all sound in Discord and also mutes your microphone. Before a meeting, check that neither button has a red line through it.</p>
{media('GIF of clicking mute and deafen and the icons changing', True)}
{note(f'Click your picture or name in the user panel to see your profile card and change your status, such as <strong>Online</strong> or <strong>Do Not Disturb</strong>.')}
''')

# ===========================================================================
# SECTION 5  COMMUNICATING
# ===========================================================================
PAGES['communicating.html'] = ('Send messages, use mentions, catch up on missed updates, and share files in Discord.', f'''
<p class="lead">This section teaches you how to talk with your group and how to make sure you never miss a meeting change or deadline.</p>
<p><strong>You need:</strong> Discord open to a text channel in your group's server.</p>
{overview('5')}
''')

PAGES['messages.html'] = ('Type, edit, reply to, and react to messages, and use direct messages and threads.', f'''
<p class="lead">Most group work in Discord happens in typed messages. This page shows you how to send, edit, and answer messages and how to talk privately.</p>

<h2>Send a message</h2>
{steps(
    'Click a text channel in the channel list.',
    'Click the message box at the bottom of the chat area. It says <strong>Message #</strong> followed by the channel name.',
    'Type your message.',
    f'Press {kbd("Enter")} to send it.',
)}
{result('Your message appears at the bottom of the chat area for everyone in the channel.')}
{note(f'To start a new line without sending, press {kbd("Shift")} + {kbd("Enter")}.')}

<h2>Edit a message you sent</h2>
{steps(
    'Hold your pointer over your message.',
    'Click the pencil icon that appears on the right.',
    'Change the text.',
    f'Press {kbd("Enter")}.',
)}
{result('The message updates and shows <strong>(edited)</strong> next to it.')}

<h2>Reply to a message</h2>
<p>A {T('reply')} shows everyone which message you are answering, which keeps busy channels clear.</p>
{steps(
    'Hold your pointer over the message you want to answer.',
    (f'Click the {ui("Reply")} arrow on the right.', media('Your screenshot of the hover menu with the Reply arrow circled', True)),
    'Type your answer.',
    f'Press {kbd("Enter")}.',
)}

<h2>React to a message</h2>
<p>A {T('reaction')} is a quick way to say "I saw this" without adding another message.</p>
{steps(
    'Hold your pointer over the message.',
    f'Click the smiley face icon ({ui("Add Reaction")}).',
    'Click an emoji, such as a thumbs up.',
)}

<h2>Send a direct message</h2>
<p>A {T('direct message')} (DM) is a private conversation outside the server channels.</p>
{steps(
    'Click a teammate\'s name in the member list.',
    f'Type your message in the {ui("Message @")} box on their profile card.',
    f'Press {kbd("Enter")}.',
)}
{result('A private conversation opens. To find it later, click the Discord logo at the top of the server list.')}

<h2>Start a thread</h2>
<p>A {T('thread')} keeps a long side discussion about one message out of the main channel.</p>
{steps(
    'Hold your pointer over the message you want to discuss.',
    f'Click the three dots ({ui("More")}).',
    f'Click {ui("Create Thread")}.',
    'Type a short name for the thread.',
    'Type your first message.',
    f'Press {kbd("Enter")}.',
)}
''')

PAGES['mentions.html'] = ('Mention a teammate, a role, or the whole server in Discord.', f'''
<p class="lead">A {T('mention')}, also called a ping, sends a notification to the people you name. Use mentions when someone needs to see a message soon.</p>

<h2>Mention a teammate</h2>
{steps(
    'In the message box, type <strong>@</strong>.',
    'Type the first few letters of your teammate\'s name.',
    (f'Click their name in the list that appears.', media('Your screenshot of the @ suggestion list above the message box', True)),
    'Finish typing your message.',
    f'Press {kbd("Enter")}.',
)}
{result('Your teammate receives a notification, and the message is highlighted for them.')}
{note('When someone mentions you, the message has a yellow highlight and a yellow bar on its left edge, so you can spot it while scrolling.')}
{media('Your screenshot of a highlighted message that mentions you')}

<h2>Mention a group of people</h2>
<p>Three special mentions reach more than one person:</p>
<table class="facts">
  <tr><th scope="col">Mention</th><th scope="col">Who is notified</th><th scope="col">When to use it</th></tr>
  <tr><td><strong>@everyone</strong></td><td>Every member of the server</td><td>Rarely, for changes that affect the whole group, such as a new meeting time</td></tr>
  <tr><td><strong>@here</strong></td><td>Only members who are online right now</td><td>For something happening now, such as "the call is starting"</td></tr>
  <tr><td><strong>@</strong> and a {T('role')} name</td><td>Only members with that role, such as @Presenters</td><td>For tasks that involve part of the group</td></tr>
</table>

{caution(f'Overusing @everyone and @here annoys teammates and can lead them to turn off notifications. Many servers allow only a {T("moderator")} to use them.')}
''')

PAGES['missed-messages.html'] = ('Catch up on missed Discord messages with unread indicators, the Inbox, pinned messages, and search.', f'''
<p class="lead">After a day away from Discord, use these four tools to find deadlines and meeting changes quickly.</p>

<h2>Unread indicators and mention badges</h2>
<ul>
  <li>An {T('unread indicator')} is a white dot to the left of a server icon or a bold channel name. It means there are new messages.</li>
  <li>A {T('mention badge')} is a red circle with a number. It means someone mentioned you, and the number shows how many times.</li>
</ul>
<p>Check channels with a red badge first, because those messages are meant for you.</p>
{media('Your screenshot of a server icon with a white dot and a red badge, and bold channel names', True)}

<h2>Use the Inbox</h2>
<p>The {T('Inbox')} collects recent mentions from every server in one list.</p>
{steps(
    'Click the tray icon at the top-right of the Discord window.',
    f'Click the {ui("Mentions")} tab.',
    f'Click {ui("Jump")} next to a message to open it in its channel.',
)}

<h2>Check pinned messages</h2>
<p>Groups often save deadlines and meeting links as a {T('pinned message', 'pinned message')}.</p>
{steps(
    'Open the channel you want to check.',
    'Click the pin icon at the top-right of the window.',
    f'Click {ui("Jump")} next to a pinned message to see it in the conversation.',
)}

<h2>Search for a message</h2>
{steps(
    'Click the <strong>Search</strong> box at the top-right of the window.',
    'Type a word from the message, such as <strong>deadline</strong>.',
    f'Press {kbd("Enter")}.',
    'Click a result to jump to that message.',
)}
{note('To search for messages from one person, type <strong>from:</strong> in the Search box, and then pick the person from the list.')}
''')

PAGES['files.html'] = ('Upload files to Discord and find shared files later.', f'''
<p class="lead">Group projects depend on drafts, slides, and images. This page shows you how to share an {T('attachment')} and how to find files your group already shared.</p>

<h2>Upload a file</h2>
{steps(
    'Open the channel where your group shares files, such as #files-and-drafts.',
    'Click the plus button on the left side of the message box.',
    f'Click {ui("Upload a File")}.',
    'Choose the file on your computer.',
    'Click <strong>Open</strong>.',
    'Type a short message that explains the file, such as "Draft of my section."',
    f'Press {kbd("Enter")}.',
)}
{result('The file appears in the channel, and teammates can open or download it.')}
{note('You can also drag a file from your desktop or a folder and drop it into the chat area.')}
{caution('Free Discord accounts have a file size limit, currently 10 MB per file. For large files, such as videos or big slide decks, upload them to OneDrive or Google Drive and paste the sharing link in Discord instead.')}

<h2>Find files later</h2>
{steps(
    'Click the <strong>Search</strong> box at the top-right of the window.',
    'Type <strong>has:</strong> in the Search box.',
    'Click <strong>file</strong> in the list.',
    f'Press {kbd("Enter")}.',
)}
{result('Discord lists every message in the server that includes a file, with the newest first.')}
{note('Ask your group to pin the final version of each file in the files channel so everyone uses the same copy.')}
''')

# ===========================================================================
# SECTIONS 6 to 9  (in progress) and GLOSSARY
# ===========================================================================
DRAFTS = {
    'notifications-privacy.html': 'This section will show you how to control how often Discord interrupts you and who can contact you.',
    'notifications.html': 'This subsection will show you how to set each server to notify you only for mentions, mute a server or channel for a set time, turn off @everyone alerts, and use Do Not Disturb during work or class.',
    'privacy-security.html': 'This subsection will show you how to limit who can send you direct messages and friend requests, block or report unwanted messages, turn on two-factor authentication, and recognize common scams.',
    'voice-and-screen.html': 'This section will show you how to attend group meetings in a voice channel and present your work by sharing your screen.',
    'voice-video.html': 'This subsection will show you how to join a voice channel, mute and deafen yourself, find the disconnect button, and turn your camera on and off.',
    'screen-share.html': 'This subsection will show you how to share one window or your entire screen, and how to stop sharing.',
    'meeting-etiquette.html': 'This subsection will list habits for smooth group calls, such as testing your microphone, closing private tabs before sharing, and muting when you are not speaking.',
    'conclusion.html': 'This section will review the skills you learned and point you toward using Discord beyond one project.',
    'checklist.html': 'This subsection will provide a checklist of core skills, such as joining a server, finding pinned messages, joining a call, sharing your screen, and setting notifications.',
    'beyond.html': 'This subsection will explain how to use the same skills in student organization servers and future classes.',
    'troubleshooting.html': 'This section will be a quick-reference guide organized by problem, so you can find a fix without rereading the tutorial.',
    'audio-video-problems.html': 'This subsection will show you what to do when others cannot hear you, when you cannot hear others, and when your camera will not turn on.',
    'channel-invite-problems.html': 'This subsection will explain what to do when you cannot see a channel or an invite link stops working.',
    'getting-help.html': 'This subsection will show you how to ask your server for help with a short description and a screenshot.',
}
for f, intro in DRAFTS.items():
    sec = next((s for s in SECTIONS if s[1] == f), None)
    PAGES[f] = (intro, '', True)

gloss = ''.join(
    f'<dt id="{re.sub(r"[^a-z0-9]+", "-", k.lower()).strip("-")}">{k[0].upper() + k[1:]}</dt><dd>{html.escape(v)}</dd>'
    for k, v in sorted(DEF.items(), key=lambda kv: kv[0].lower()))
PAGES['glossary.html'] = ('Plain-language definitions of every new Discord word in this tutorial.', f'''
<p class="lead">This glossary defines every new word in this tutorial in alphabetical order. The same definitions appear when you point to a blue word on any page.</p>
<p>More words will be added as the remaining sections are written.</p>
<dl class="glossary">{gloss}</dl>
''')

# ---------------------------------------------------------------------------
# Write files
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    for f in glob.glob('*.html'):
        os.remove(f)
    for num, f, title, *_ in ORDER:
        entry = PAGES[f]
        desc, body = entry[0], entry[1]
        draft = len(entry) > 2 and entry[2]
        body = number_media(body, num)
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(page(f, body, desc, draft))
    # Old addresses from the first draft redirect to the new pages
    for old, new in {'create-account.html': 'getting-started.html', 'join-server.html': 'joining-a-server.html', 'what-is-discord.html': 'index.html'}.items():
        with open(old, 'w', encoding='utf-8') as fh:
            fh.write(f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0; url={new}">'
                     f'<link rel="canonical" href="{new}"><title>Moved</title></head><body><p>This page moved to <a href="{new}">{new}</a>.</p></body></html>')
    print('Built', len(ORDER), 'pages')
