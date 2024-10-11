# examples.py

def truncate_text(text, max_length):
    if len(text) <= max_length:
        return text, ''
    else:
        cutoff = text.rfind(' ', 0, max_length)
        if cutoff == -1:
            cutoff = max_length
        short_text = text[:cutoff]
        remaining_text = text[cutoff:].lstrip()
        return short_text, remaining_text

# Source links
sources = [
    "https://coingape.com/edpb-report-criticizes-chatgpt-gdpr-compliance/",
    "https://readwrite.com/meta-ai-europe-complaints-data-privacy/",
    "https://www.mirror.co.uk/news/us-news/self-driving-tesla-bashes-cop-33034235",
    "https://www.kbb.com/car-news/fisker-recalls-all-its-2023-cars/",
    "https://cybersecuritynews.com/ai-assistant-rabbit-r1s-code-vulnerability/",
    "https://jerseyeveningpost.com/news/2024/05/13/ai-could-be-used-in-jerseys-new-major-crackdown-on-scammers/"
]

# Example texts
example_texts = [
    "Several European countries have issued temporary stop orders on ChatGPT, urging OpenAI to accelerate its compliance adjustments. The European Data Protection Board (EDPB) recently published a report that highlights significant shortcomings in OpenAI's ChatGPT's compliance with the General Data Protection Regulation (GDPR). The assessment underscores ongoing challenges, particularly with the model's accuracy and transparency. OpenAI has introduced various measures to align ChatGPT with GDPR's transparency principle. However, the EDPB considers these efforts to be revised.",
    "Meta emphasized the need to train AI on European data but faced criticism for auto-opting users into AI training. Meta has postponed the launch of its AI models in Europe following guidance from Ireland's privacy regulators to delay its plans to use data from Facebook and Instagram users, according to the U.S. social media company's announcement on Friday. The Irish Data Protection Commission (DPC) requested that the tech giant delay training its large language model on behalf of the European data protection authorities. Meta said on its site that it was disappointed by the decision. 'This is a step backwards for European innovation, competition in AI development and further delays bringing the benefits of AI to people in Europe,' the company said.",
    "A man operating a self-driving Tesla crashed into a cop car on Thursday morning as he admitted to being on his phone. As an Orange County police officer was investigating a deadly crash on a busy highway, a man operating a self-driving Tesla ploughed into his patrol vehicle. The driver, who has not been identified, was using his Tesla's semi-autonomous self-driving mode, which assists with braking, steering and changing lanes but that isn't fool proof, when the vehicle veered into the cruiser, narrowly missing the cop, who was directing traffic. He was reportedly able to jump out of the way. Another officer was reportedly inside the vehicle -- neither sustained injuries. The man got out of the blue vehicle, The Los Angeles Times reported, and cooperated with the investigation -- he admitted to being on his phone at the time of the crash, somehow failing to notice the flares and bright, flashing police lights at the scene where at least one person died in another crash.",
    "Troubled electric car startup Fisker has recalled every 2023 Fisker Ocean (the only car it sells) to correct warnings that don't comply with federal safety laws. Fisker tells the National Highway Traffic Safety Administration that 'the instrument panel displays the incorrect font size of the Brake, Park, and Antilock Brake System (ABS) warning lights and displays certain warning lights in amber instead of red.' The incorrect colors and fonts could fail to alert owners to a problem. 'Additionally, multiple warning lights fail to illuminate during the ignition cycle bulb check,' the company says. Since all Fisker Oceans use digital screens for their driver's displays, Fisker can fix the problem remotely with a software update.",
    "Rabbitude, a group of developers and researchers, has exposed a security vulnerability in Rabbit's R1 AI assistant. The group discovered that API keys were hardcoded into the company's codebase, a practice that is widely considered a major security flaw. These keys provided access to Rabbit's accounts with third-party services, including its text-to-speech provider ElevenLabs and its SendGrid account, which is used for sending emails from the rabbit.tech domain. According to Rabbitude, access to these API keys, particularly the ElevenLabs API, meant that they could access every response ever given by R1 devices. This breach of privacy is alarming, as it exposes sensitive user data to potential misuse.",
    "A MAJOR crackdown on scams - potentially using AI to identify fraudulent activity - is being launched following a surge in organised-crime gangs conning Islanders out of their life savings. Police chief Robin Smith recently met more than 30 senior representatives from banks, as well as cyber-crime and telephone companies, at the States police's headquarters to discuss how to better collaborate on catching sophisticated scammers and protect Islanders' money. Techniques under development include using AI to identify fraudsters and stop unwanted calls, circulating warnings more quickly, 'killing' scam numbers and setting up an incident room which could deal with new trends more quickly. Mr Smith said: 'If we could stop half of the scams currently going on, which would be a tremendous result, that would mean a lot fewer losses and a lot fewer victims.' Sophisticated frauds sweeping the Island have been on the rise over the past year, and national figures show that these now account for around 40% of all crime."
]

# Combine texts and sources
examples_raw = list(zip(example_texts, sources))

examples = []

for idx, (text, source) in enumerate(examples_raw, start=1):
    short_text, remaining_text = truncate_text(text, 80)
    examples.append({
        'short': short_text,
        'rest': remaining_text,
        'source': source
    })
