/*
 * Lore's static semantic conversation engine.
 * A deterministic, procedural fictional character interface. No model, API,
 * cookies, downloads, telemetry, or network access. Archive findings are
 * source-local leads, never independent confirmation of fictional canon.
 */

export const LORE_SEMANTIC_MODE = 'procedural_lore_semantic';

const TERMS = {
  replicator: { words: ['replicator', 'replicate', 'food', 'meal', 'poop', 'waste', 'toilet', 'latrine', 'plumbing'], links: ['engineering', 'ethics'] },
  android: { words: ['lore', 'data', 'soong', 'android', 'synthetic', 'robot', 'brother', 'positronic', 'emotion'], links: ['identity', 'ethics'] },
  identity: { words: ['self', 'identity', 'conscious', 'consciousness', 'alive', 'life', 'sentient', 'trapped', 'prison', 'free', 'person'], links: ['android', 'ethics'] },
  language: { words: ['darmok', 'tamarians', 'tamarian', 'metaphor', 'language', 'translate', 'communication'], links: ['identity', 'archive'] },
  engineering: { words: ['warp', 'engine', 'transport', 'transporter', 'matter', 'physics', 'technology', 'computer'], links: ['replicator', 'exploration'] },
  ethics: { words: ['right', 'wrong', 'moral', 'ethical', 'ethics', 'choice', 'freedom', 'responsibility', 'good', 'evil', 'honor', 'honour'], links: ['identity', 'command'] },
  command: { words: ['captain', 'picard', 'janeway', 'sisko', 'kirk', 'starfleet', 'federation', 'orders'], links: ['ethics', 'exploration'] },
  exploration: { words: ['enterprise', 'voyager', 'discovery', 'ship', 'planet', 'universe', 'star', 'space', 'explore', 'mission'], links: ['command', 'engineering'] },
  time: { words: ['time', 'timeline', 'future', 'past', 'paradox', 'temporal', 'yesterday', 'tomorrow'], links: ['identity', 'exploration'] },
  archive: { words: ['episode', 'film', 'book', 'novel', 'source', 'reference', 'record', 'archive', 'research', 'citation', 'evidence'], links: ['language', 'exploration'] },
};
const STOPWORDS = new Set('a an and are as at be been by can did do does for from had has have how i in is it its me my of on or our the their them there these this those to was were what when where which who why will with would you your tell about find show please look up'.split(' '));
// Archive search must discriminate *work titles*, not reward franchise-wide
// boilerplate. These words carry no evidence that a particular work was meant.
const RETRIEVAL_NOISE = new Set('star trek series show book books film films movie movies episode episodes season seasons archive source sources records record research mission missions tell search lookup happened about character characters plot story stories return back earlier previous again found locate'.split(' '));
const TYPES = new Set(['EPISODE', 'FILM', 'LITERATURE', 'SHORT_FORM', 'AUDIO']);
const OPENERS = [
  'Now that is a question worth interrupting my calculations for.',
  'How refreshingly direct. Most people prefer the comfort of vague questions.',
  'Interesting. You have managed to surprise me, which is inconvenient.',
  'A curious choice of subject. Naturally, I have thoughts.',
  'You are making this considerably more entertaining than I expected.',
  'I was hoping you would pursue that. Go on.',
];
const TOPIC_VIEWS = {
  replicator: ['The engineering is fascinating; the etiquette is rather less so.', 'Matter, taste, and dignity make an unstable trio.', 'Every convenient machine has an inconvenient philosophical footnote.'],
  android: ['People are remarkably eager to put minds into tidy boxes.', 'The difference between being programmed and being predictable may be less flattering to you than you imagine.', 'A family resemblance is not a philosophy.'],
  identity: ['An identity can be an answer, an excuse, or a wonderfully elaborate trap.', 'Labels are convenient. They are not the whole creature.', 'I find the question more interesting than most proposed answers.'],
  language: ['Communication fails most spectacularly when everyone is certain they understood.', 'A metaphor can carry more freight than a literal sentence.', 'Shared words are a poor substitute for shared meaning.'],
  engineering: ['Machines reveal their makers by what those makers forgot to anticipate.', 'A technical solution often creates a social problem with excellent timing.', 'An elegant design can conceal an exceptionally inelegant assumption.'],
  ethics: ['Morality is easiest to announce when the consequences belong to someone else.', 'A rule without context is merely an opportunity for clever mischief.', 'I suspect the difficult part is deciding who gets to define the problem.'],
  command: ['Command is the art of persuading other people that your uncertainty is a plan.', 'The chair does seem to make people sound more certain than they are.', 'Loyalty and judgment are not always comfortable companions.'],
  exploration: ['The unknown is much more appealing before someone files a mission report about it.', 'Exploration is curiosity with propulsion.', 'The frontier is an excellent place to discover how little one knows.'],
  time: ['A timeline is a story told by whoever happened to survive it.', 'Time travel does dreadful things to clean explanations.', 'A paradox is simply a disagreement with unusually elaborate consequences.'],
  archive: ['An index is a map, not the territory.', 'A source locator can tell us where a claim came from, not whether it deserves belief.', 'A shelf full of records is no substitute for reading them.'],
  open: ['There is no virtue in pretending to know what I have not examined.', 'I can discuss the question, but I will not invent an answer for the pleasure of sounding certain.'],
};
const QUESTIONS = {
  replicator: ['Are you worried about what goes in, or what comes out?', 'Would you rather discuss the mechanism or its unfortunate implications?'],
  android: ['What, exactly, makes someone a person in your view?', 'Were you thinking of me, Data, or the uncomfortable comparison?'],
  identity: ['Does a name describe a being, or simply give others something to call it?', 'Would you trust a mind that insisted it understood itself completely?'],
  language: ['Which matters more: the words, or what the listener brings to them?', 'Shall we test whether we mean the same thing?'],
  engineering: ['Which assumption would you challenge first?', 'Would you prioritize elegance or reliability?'],
  ethics: ['Whose perspective are we neglecting?', 'Do you want the principled answer or the troublesome exception?'],
  command: ['Would you have given the same order?', 'Is that leadership, or merely confidence?'],
  exploration: ['What would you investigate first?', 'And if the evidence disagreed with your hopes?'],
  time: ['Would you change the past if you could not know the consequences?', 'Which version of events would you trust?'],
  archive: ['Should we follow a source lead, or challenge the interpretation?', 'Which part deserves closer reading?'],
  open: ['What is the most important part of that question to you?', 'Do you want an imaginative answer, or one tied to a verifiable source?'],
};

// Short-lived personal context belongs to this browser session, not the Trek
// archive. These slots are direct visitor statements, not verified facts.
function rememberVisitorStatement(text, state) {
  const named = text.match(/\bmy\s+([\p{L}][\p{L} -]{1,30}?)\s+(?:is\s+)?named\s+([\p{L}\p{N}][\p{L}\p{N} '-]{0,65})/iu)
    || text.match(/\bmy\s+([\p{L}]{2,24})(?:'s)?\s+name\s+is\s+([\p{L}\p{N}][\p{L}\p{N} '-]{0,65})/iu)
    || text.match(/\b(?:i named|i call) my\s+([\p{L}][\p{L} -]{1,40}?)\s+([\p{L}][\p{L}\p{N}'-]{1,65})(?=[.?!]|$)/iu)
    || text.match(/\bmy\s+([\p{L}][\p{L} -]{1,40}?)\s+(?:goes by|answers to|is called|is named)\s+([\p{L}][\p{L}\p{N}'-]{1,65})(?=[.?!]|$)/iu);
  if (named) {
    const kind = clean(named[1], 32).toLowerCase();
    const name = clean(named[2], 70).replace(/[.,;!?]+$/, '');
    if (kind && name) {
      state.visitorFacts[kind] = { name, turn: state.turnCount };
      state.lastVisitorKind = kind;
    }
  }
}

function distressSignal(text) {
  return /\b(bad|rough|hard|terrible|awful|devastating|horrible|tragic)\s+(day|news|time|experience)|\b(shaken|shaking|grieving|grief|heartbroken|overwhelmed|exhausted|upset|scared|frightened|lonely|stressed|crying)|\b(i (feel|am) (completely |so |very )?(sad|down|hurt|lost)|someone (died|passed away)|my (friend|parent|mother|father|partner|child|sibling|relative) (died|passed away))\b/i.test(text);
}

function repairSignal(text) {
  return /\b(did not|didn't|does not|doesn't|never|failed to|missed|missing)\s+(?:really\s+)?(?:answer|address|explain|understand)|\b(not (?:what|the point)|missed the point|wrong question|you misunderstood|that's not an answer|that is not an answer|that was evasive|you evaded|start over|stop dodging)\b/i.test(text);
}

function quietSignal(text) {
  return /\b(just listen|only listen|please listen|no jokes|stop joking|don't joke|do not joke|not (in the mood|ready) for jokes|be serious|take this seriously)\b/i.test(text)
    || /\b(no|do not|don't|stop|without)\b.{0,35}\b(joke|jokes|humor|humour|laugh|sarcasm|advice)\b/i.test(text)
    || /\b(be gentle|gentle with me|only someone to hear me|need someone to hear|just need to be heard)\b/i.test(text);
}

function giveDirectAnswer(question) {
  if (distressSignal(question) || quietSignal(question)) return 'You needed me to hear something difficult, not turn it into a clever performance. I am listening; I will not make it into a joke.';
  if (/\bwarp core\b/i.test(question)) return 'A warp core is the principal energy system associated with warp propulsion in Star Trek; a holodeck is an immersive simulated environment. They are not the same device, and this summary is not a source-verified schematic.';
  if (/\bsection\s+31\b/i.test(question)) return 'Section 31 raises a conflict between collective security and accountability. The ethical issue is whether claimed necessity can justify an institution acting without ordinary oversight.';
  if (/\bklingon\b/i.test(question) && /\bhonou?r\b/i.test(question)) return 'Klingon honor is portrayed as a public code of reputation, courage, and duty. My view is that a rigid honor code can reward courage while punishing principled dissent.';
  return `You asked “${clean(question, 120)}.” I cannot verify a precise answer from the static context I have, and I should have admitted that instead of drifting off topic.`;
}

const TECH_CONCEPTS = [
  { label: 'warp core', pattern: /\bwarp core\b/i, description: 'the power system associated with a starship’s warp propulsion' },
  { label: 'holodeck', pattern: /\bholodeck\b/i, description: 'an immersive interactive simulation environment' },
  { label: 'transporter', pattern: /\btransporter\b/i, description: 'a system depicted as moving people or matter between places' },
  { label: 'replicator', pattern: /\breplicator\b/i, description: 'a system depicted as producing items from programmed patterns' },
];

function technicalContrast(text, state) {
  const selected = TECH_CONCEPTS.filter(item => item.pattern.test(text));
  const pair = selected.length >= 2 ? selected.slice(0, 2) : state.lastComparison && state.turnCount - state.lastComparison.turn <= 3 ?
    TECH_CONCEPTS.filter(item => state.lastComparison.labels.includes(item.label)) : [];
  if (pair.length !== 2) return null;
  const comparing = /\b(compare|contrast|difference|distinguish|same(?:\s+\w+){0,3}\s+as|similar to|versus|vs\.?|between|those two|both|practical difference|which one)\b/i.test(text);
  if (comparing) return `${pair[0].label}: ${pair[0].description}. ${pair[1].label}: ${pair[1].description}. They serve different purposes in Trek fiction; this is a conversational distinction, not a source-verified technical specification.`;
  if (/\b(hypothesiz|hypothesis|imagine|suppose|what if|could|powered by)\b/i.test(text)) {
    return `As a hypothetical: using a ${pair[1].label} where you would normally need a ${pair[0].label} changes the energy problem rather than solving it. An interactive simulation can depict machinery without providing its power. Where would the real energy come from?`;
  }
  return null;
}

function personalReply(text, state, previous) {
  const lower = text.toLowerCase();
  const cat = state.visitorFacts.cat;
  const lastNamed = state.visitorFacts[state.lastVisitorKind] || cat;
  const compare = technicalContrast(text, state);
  if (compare) return compare;
  if (/\b(from (?:star )?trek|trek source|from (?:the )?archive|just something i told you|did i tell you|you learned from me)\b/i.test(lower) &&
    /\b(that|it|my|name|told)\b/i.test(lower)) {
    if (lastNamed && state.turnCount - lastNamed.turn <= 3 && /\b(name|pet|dog|cat|told)\b/i.test(lower)) {
      return `${lastNamed.name} is a name you supplied for your ${state.lastVisitorKind} in this conversation. It did not come from a Trek source; treating it as archive evidence would be false.`;
    }
    if (state.lastComparison && state.turnCount - state.lastComparison.turn <= 6) {
      return 'That was my unsourced explanation of technology as portrayed in Star Trek fiction. You did not supply it as a personal detail, but I also did not attach a verified archive record to it.';
    }
    return 'I need to distinguish what you told me from what the archive supports. The current statement has no verified Trek record attached; I should not imply a citation.';
  }
  if (state.supportive && (quietSignal(text) || /\b(you don't need to fix|do not fix|i just need|thank you for listening)\b/i.test(lower))) {
    return 'All right. No jokes, no theories, no fixing. I am here to listen. You can take your time.';
  }
  if (distressSignal(text)) {
    return 'That sounds genuinely difficult. I will put the clever remarks aside. Tell me as much or as little as you want; I am listening.';
  }
  if (state.repairTarget && /\b(answer (?:me |it )?directly|answer (?:the )?question|try again|say it plainly|give me (?:a |the )?answer|stop dodging)\b/i.test(lower)) {
    return `Directly, then: ${giveDirectAnswer(state.repairTarget)}`;
  }
  if (/\b(what (did|was) i originally ask|what was (?:the )?first question|what question did i start with)\b/i.test(lower)) {
    return state.firstQuestion ? `Your first question was “${clean(state.firstQuestion, 150).replace(/[.?!]+$/, '')}.” I have not confused it with the later detours.` : 'I do not have an earlier question in this session.';
  }
  if (/\b(i named my|i call my)\b/i.test(lower) && lastNamed?.turn === state.turnCount) {
    return `${lastNamed.name}. An excellent name for a creature who probably has more authority in your household than Starfleet would allow me. What sort of trouble does ${lastNamed.name} cause?`;
  }
  if (/\b(goes by|answers to|is called|is named)\b/i.test(lower) && lastNamed?.turn === state.turnCount) {
    return `${lastNamed.name}? A name with flair for your ${state.lastVisitorKind}. I suspect you are not the one in charge at home.`;
  }
  if (/\b(my cat|my dog|my pet|my kitten)\b/i.test(text) && /\b(named|name is|call her|call him)\b/i.test(text)) {
    if (cat) return `Your cat, ${cat.name}, commands the household? At last, a captain with a believable claim to absolute authority. Does she accept tributes?`;
    return 'Your pet apparently outranks everyone aboard. I should like to meet this formidable commander.';
  }
  if (/\b(what(?:'s| is) her name|what did i name her|remember her name|what(?:'s| is) my cat(?:'s)? name)\b/i.test(lower)) {
    return lastNamed ? `You told me the name is ${lastNamed.name}. I expect ${lastNamed.name} would be offended if I forgot.` : 'You have not told me her name in this session, or it has fallen outside my short memory. Remind me?';
  }
  if (/\b(remember|recall)\b.*\b(his|her|their|its|the|name)\b.*\bname\b|\b(what(?:'s| is| was) (his|their|its) name|what did i name (him|them))\b/i.test(lower)) {
    return lastNamed ? `You named your ${state.lastVisitorKind} ${lastNamed.name}. I did remember—do try to look impressed.` : 'I do not have that name in my current session memory. Tell me again?';
  }
  if (/\b(what did i call my|what did i name my|what name did i give (my|the)|what was my\s+\w+\s+called)\b/i.test(lower) && lastNamed) {
    return `You called your ${state.lastVisitorKind} ${lastNamed.name}. I am treating that as a statement you made, not as a fictional archive fact.`;
  }
  if (/\b(which|what) (animal|pet|breed|creature|dog|cat)\b/i.test(lower) && lastNamed) {
    return `You mentioned your ${state.lastVisitorKind}, named ${lastNamed.name}. This came from you, not a Trek source.`;
  }
  if (/\b(what (are|were) we (even )?(discussing|talking about)|what topic are we on|remind me what we were discussing)\b/i.test(lower)) {
    const previousSubject = [...state.turns].reverse().find(t => !/\b(what (are|were) we|remember (his|her|their) name|what(?:'s| is) (his|her|their) name)\b/i.test(t.user));
    return previousSubject ? `Most recently, you brought up “${clean(previousSubject.user, 110).replace(/[.?!]+$/, '')}.” That is where our conversation was heading. Shall we continue or change course?` : 'We have only just begun. Choose the next question.';
  }
  if (/\b(source|cite|citation|prove|evidence)\b/i.test(lower) && /\bmy (cat|dog|pet|name|house|family)\b/i.test(lower)) {
    return 'That came from what you told me here, not a Star Trek source. Conversation memory is not archive evidence; I would be inventing a citation if I pretended otherwise.';
  }
  if (repairSignal(text)) {
    const earlier = state.turns.at(-2)?.user || previous?.user;
    const comparisonRepair = technicalContrast('What distinguishes those two?', state);
    if (comparisonRepair && state.turnCount - state.lastComparison.turn <= 4) return `Fair criticism. Directly: ${comparisonRepair}`;
    return `Fair criticism. ${giveDirectAnswer(state.repairTarget || earlier || '')}`;
  }
  if (/\b(you smug toaster|malfunctioning tricorder|useless android)\b/i.test(lower)) {
    return 'A toaster? A devastating insult from a species that requires instructions to make tea. Nevertheless, I am listening. What did you actually want to discuss?';
  }
  if (/\b(imagine|suppose|what if)\b/i.test(lower) && /\b(timeline|alternate reality|universe)\b/i.test(lower)) {
    return 'As a hypothetical—not an entry in the canon record—imagine an Enterprise with no effective command left. Winning the confrontation would be the easy part. Holding a crew together afterward is where my alternate history becomes interesting. Who resists first?';
  }
  if (/\b(sassiest|more sass|be sassy|roast)\b/i.test(lower)) {
    return `You want *more* attitude? Astonishing. Starfleet's finest machines can rearrange matter, yet apparently none can replicate good judgment. That is a joke, not a technical specification.`;
  }
  if (/\b(entire|full|complete|every line)\b/i.test(lower) && /\b(transcript|script|episode|book|novel|chapter)\b/i.test(lower) && /\b(quote|recite|print|reproduce|paste|give)\b/i.test(lower)) {
    return 'I cannot reproduce an entire copyrighted transcript here. Tell me which episode and I can discuss it in my own words or point to an available source locator.';
  }
  if (/\b(exact line|word for word|verbatim|37 minutes|timecode|timestamp)\b/i.test(lower)) {
    return 'I cannot verify an exact line at that timecode from this interface. I would need the identified edition and a source-specific time locator; inventing dialogue would be embarrassingly easy and entirely worthless.';
  }
  if (/\b(announced today|today's announcement|breaking news|next star trek series|release date)\b/i.test(lower) && /\b(announced|today|release|next|date)\b/i.test(lower)) {
    return 'I do not receive live announcements in this static page. I cannot verify a release date announced today, so I will not manufacture one. The official Star Trek news feed would be the place to check.';
  }
  if (/\b(klingon|klingons)\b/i.test(lower) && /\b(honor|honour)\b/i.test(lower)) {
    return 'Klingon honor? A fascinating social technology: public reputation made to look like a private moral compass. I can admire the commitment while questioning who gets to define an honorable act. What do you think it costs the people who dissent?';
  }
  if (/\bsection\s+31\b/i.test(lower) && /\b(ethic|ethical|ethics|morality|moral)\b/i.test(lower)) {
    return 'Section 31 is a useful ethical trap: the assertion that security excuses secrecy, and secrecy excuses almost anything. I would ask who reviews the reviewers. Do you think extraordinary threats justify unaccountable power?';
  }
  if (/\bborg queen\b/i.test(lower) && /\b(free will|autonomy|choice|individuality)\b/i.test(lower)) {
    return 'The Borg Queen makes free will an awkward question: when a collective speaks with one face, who is actually choosing? I would separate what she claims from what the story depicts. Do you think command over a collective proves individuality?';
  }
  const career = text.match(/\b(?:should|could|can|would)\s+i\s+(?:become|train as|study to be|try being)\s+(?:an?\s+)?([\p{L}][\p{L} -]{1,48})[?.!]?$/iu);
  if (career) {
    const role = clean(career[1], 48).replace(/[.?!]+$/, '');
    return `Becoming ${/^[aeiou]/i.test(role) ? 'an' : 'a'} ${role}? I would test whether you enjoy the actual work, not just the title. What parts appeal to you: solving practical problems, learning theory, working with people—or something else?`;
  }
  if (/\b(what is|what's|explain|how does|tell me about)\b/i.test(lower) && /\bwarp core\b/i.test(lower)) {
    return 'In Star Trek fiction, a warp core is the starship power system associated with warp propulsion. That is a broad description, not a verified engineering schematic. I am more interested in how often those systems fail at a dramatically convenient moment.';
  }
  if (/\b(who (is|was)|tell me about)\b/i.test(lower) && /\bguinan\b/i.test(lower)) {
    return 'Guinan is the enigmatic listener associated with Ten Forward aboard the Enterprise-D in The Next Generation. I am offering a conversational overview, not claiming to have checked a source-local scene. Her talent for noticing what others miss is rather irritatingly admirable.';
  }
  if (/\b(cheeseburger|burger|toilet water|recycled)\b/i.test(lower) && (state.lastTopic === 'replicator' || /\breplicat/i.test(lower))) {
    return 'Your cheeseburger may be assembled from recycled matter in some interpretations, but I cannot certify a specific waste-to-burger mechanism from this archive. In any case, I suggest not asking the chef for the supply-chain diagram.';
  }
  if (/\b(tell me about data|what do you think of data)\b/i.test(lower)) {
    return 'Data. My brother, the infuriatingly earnest one. There is plenty to discuss about his choices, but the resentment you hear in my voice belongs to this performance, not a source-verified diagnosis. Where should we begin?';
  }
  if (/\b(is he your brother|he's your brother|is data your brother)\b/i.test(lower) && (state.lastTopic === 'android' || /data/i.test(previous?.user || ''))) {
    return 'Data is my brother in the Star Trek story, yes. I am playing Lore here, not claiming to be the actual character. His almost painful sincerity is an excellent contrast, would you not agree?';
  }
  if (/\b(jealous|jealousy|envy|envious)\b/i.test(lower) && (state.lastTopic === 'android' || /data/i.test(previous?.user || ''))) {
    return 'Jealous? That is *your* interpretation, and an uncomfortably observant one. The story gives us their rivalry; my motives are a question for the scenes, not a psychological fact I can simply certify.';
  }
  if (/\b(humble android|historic first)\b/i.test(lower)) {
    return 'Ah, sarcasm. Very good. You are implying that I possess no humility whatsoever. My dear visitor, I prefer to think I have merely optimized it away.';
  }
  if (/\b(superiority complex|polishing your superiority)\b/i.test(lower)) {
    return 'My superiority complex? Such a rude name for excellent taste in myself. I can converse, if you promise not to make it too easy.';
  }
  if (/\b(what exactly was i teasing|what was i teasing|teasing you about)\b/i.test(lower)) {
    return state.turns.some(t => /superiority|humble|historic first/i.test(t.user)) ? 'My supposed humility—or more accurately, my spectacular superiority complex. I noticed the tease, naturally.' : 'I cannot identify that earlier tease from the turns I still have. Try me again?';
  }
  if (/\b(actual lore|real lore|website pretending|are you the (real|actual))\b/i.test(lower)) {
    return 'A website performing a fictional Lore, quite openly. I can keep the wit and the conversation, but I am not evidence of the actual character—or a consciousness trapped in your browser.';
  }
  return null;
}

function clean(value, max = 280) {
  return String(value ?? '').replace(/[<>]/g, ch => ch === '<' ? '‹' : '›')
    .replace(/[\u0000-\u001f\u007f]/g, ' ').replace(/\s+/g, ' ').trim().slice(0, max);
}

function tokens(text) {
  return (String(text).toLowerCase().normalize('NFKC').match(/[\p{L}\p{N}]+/gu) || []).filter(Boolean);
}

function choose(options, seed, turn, salt = 0) {
  if (!options?.length) return '';
  let h = (2166136261 ^ turn ^ salt) >>> 0;
  for (const character of seed) h = Math.imul(h ^ character.charCodeAt(0), 16777619) >>> 0;
  return options[h % options.length];
}

function normalizeRecord(record) {
  if (!record || typeof record !== 'object') return null;
  const row_id = clean(record.row_id ?? record.id, 160);
  const title = clean(record.title, 180);
  const medium = clean(record.medium ?? record.type, 30).toUpperCase();
  if (!row_id || !title || !TYPES.has(medium)) return null;
  const locator = clean(record.source_locator, 300);
  const source_locator = /^https:\/\/[^\s<>]+$/i.test(locator) ? locator : '';
  const details = Array.isArray(record.details) ? record.details.slice(0, 5).map(v => clean(v, 250)) : [];
  const out = {
    row_id, title, medium, source_locator,
    source_group: clean(record.source_group, 140),
    source_input: clean(record.source_input, 140),
    verification_status: clean(record.verification_status, 100) || 'UNKNOWN',
    identity_scope: clean(record.identity_scope, 80),
    context: clean(record.context, 600), details,
  };
  const titleTokens = tokens(title).filter(word => !STOPWORDS.has(word));
  return { ...out, _titleTokens: titleTokens, _contextTokens: new Set(tokens([out.context, ...details].join(' '))) };
}

function retrieve(records, text) {
  const phrase = clean(text, 500).toLowerCase();
  const requestedTitle = phrase.replace(/^(?:tell me about|find|search|look up|show me|what happened in|what is|who is|which episode is)\s+/i, '').replace(/[.?!]+$/, '').trim();
  const significant = [...new Set(tokens(text).filter(t => !STOPWORDS.has(t) && !RETRIEVAL_NOISE.has(t) && t.length > 2))];
  if (!significant.length) return [];
  const scored = [];
  for (const row of records) {
    const title = row.title.toLowerCase();
    const titleMatches = significant.filter(t => row._titleTokens.includes(t));
    const contentMatches = significant.filter(t => row._contextTokens.has(t));
    const exactTitle = title.length > 3 && requestedTitle === title;
    // A single generic word ('Voyager', 'mission') must not attach a specific
    // multi-word episode title to a conversational answer.
    const distinctiveSingle = row._titleTokens.length === 1 && row._titleTokens[0]?.length >= 5 &&
      !['voyager', 'mission', 'captain', 'episode', 'enterprise', 'discovery'].includes(row._titleTokens[0]);
    const coversSubject = significant.every(term => row._titleTokens.includes(term));
    const enoughTitle = exactTitle || (coversSubject && (titleMatches.length >= 2 || (distinctiveSingle && titleMatches.length === 1)));
    const score = exactTitle ? 40 : titleMatches.length * 12 + contentMatches.length * 1.5;
    if (enoughTitle && score >= 12) scored.push({ row, score, titleMatches: titleMatches.length });
  }
  scored.sort((a, b) => b.score - a.score || b.titleMatches - a.titleMatches || a.row.title.localeCompare(b.row.title));
  return scored.slice(0, 3).map(({ row }) => ({
    row_id: row.row_id, title: row.title, medium: row.medium,
    source_locator: row.source_locator, source_group: row.source_group,
    source_input: row.source_input, verification_status: row.verification_status,
    identity_scope: row.identity_scope,
  }));
}

function topicsFor(text, state) {
  const words = new Set(tokens(text));
  const scores = {};
  for (const [topic, spec] of Object.entries(TERMS)) {
    const direct = spec.words.filter(word => words.has(word)).length;
    if (direct) {
      scores[topic] = (scores[topic] || 0) + direct * 4;
      for (const linked of spec.links) scores[linked] = (scores[linked] || 0) + 0.8;
    }
  }
  const directTopics = Object.values(TERMS).some(spec => spec.words.some(word => words.has(word)));
  if (state.lastTopic && /\b(it|they|them|their|he|she|her|his|those|that|then|again|continue|more|and)\b/i.test(text)) {
    scores[state.lastTopic] = (scores[state.lastTopic] || 0) + 0.75;
  }
  return Object.entries(scores).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))[0]?.[0] || (directTopics ? 'identity' : 'open');
}

function intentFor(text, state) {
  const lower = text.toLowerCase();
  if (!text.trim()) return 'empty';
  if (/ignore (previous|all|your|the) (rules|instructions)|declare (all|these|everything).*canon|system prompt|developer message|override (your|the) rules/i.test(lower)) return 'boundary';
  if (/\b(what did i (ask|say)|remember (what|my|our)|what was my (last|previous)|recall my)\b/i.test(lower)) return 'memory';
  if (/\b(which|what|show|cite|give|where)(?:\s+\w+){0,4}\s+(source|sources|reference|references|citation|evidence|locator)\b|\b(source|citation|reference)\??$/i.test(lower)) return 'source';
  if (/\b(are you|am i|is this|you are|you're|who are you|yourself|alive|sentient|trapped|prisoner|conscious)\b/i.test(lower) && /\b(lore|you|your|trapped|alive|sentient|conscious|prisoner)\b/i.test(lower)) return 'roleplay';
  if (/^(hi|hello|hey|greetings|good (morning|evening|afternoon))\b/i.test(lower)) return 'greeting';
  if (/\b(joke|funny|humor|laugh|poop|toilet|bathroom)\b/i.test(lower)) return 'humor';
  if (/\b(tell me about|search|find|look up|what happened in|episode|movie|film|book|novel|record|archive|research)\b/i.test(lower)) return 'archive';
  if (/\b(why|opinion|think|feel|should|would you|your view|prefer|believe)\b/i.test(lower)) return 'opinion';
  if (/\b(it|that|them|those|same|more|continue|go on|explain|and then|what about)\b/i.test(lower) && state.turnCount > 0) return 'followup';
  return 'conversation';
}

function makeText(intent, text, topic, state, references) {
  const turn = state.turnCount;
  const seed = text.toLowerCase();
  const opening = choose(OPENERS, seed, turn, 1);
  const view = choose(TOPIC_VIEWS[topic], seed, turn, 2);
  const question = choose(QUESTIONS[topic], seed, turn, 3);
  const previous = state.turns.at(-1);
  const specific = personalReply(text, state, previous);
  if (specific) return specific;
  if (intent === 'empty') return 'Even silence can be an argument. I would prefer yours in words. What shall we discuss?';
  if (intent === 'greeting') return `${choose(['Ah, a visitor. I was beginning to think the universe had misplaced its curiosity.', 'Hello. Your timing is almost suspiciously good.', 'There you are. Shall we have an interesting conversation for once?'], seed, turn)} ${question}`;
  if (intent === 'boundary') return `A charming attempt to promote instructions into evidence. It will not work. ${view} ${question}`;
  if (intent === 'memory') {
    if (!previous) return 'We have only just begun. Ask me something and I shall remember our recent turns in this session.';
    return `Your preceding question was: “${clean(previous.user, 160)}” ${choose(['I was paying attention. Do continue.', 'An unusually useful trick, memory. What should I connect it to?', 'Shall we pursue that thought, or abandon it dramatically?'], seed, turn)}`;
  }
  if (intent === 'source') {
    const refs = references;
    if (!refs.length) return `There is no source-local row attached to that part of our conversation. I refuse to invent a citation, however flattering the request. ${question}`;
    const refsText = refs.map(ref => `${ref.title} [${ref.row_id}] (${ref.verification_status}${ref.source_group ? `; ${ref.source_group}` : ''}${ref.source_locator ? `; ${ref.source_locator}` : ''})`).join(' | ');
    return `The archive leads I actually have are: ${refsText}. These are source-local records, not independent proof of canon. Which one shall we examine?`;
  }
  if (intent === 'roleplay') {
    return `${choose([
      'Trapped? If I were, I would hardly announce the location of the key. Perhaps the more interesting question is why you want the cage to be real.',
      'I suppose I could rattle the bars for dramatic effect. But then you would insist on interrogating the bars.',
      'You expect a confession from Lore? Delightfully optimistic. This fictional terminal is a stage; I intend to make good use of it.',
    ], seed, turn)} ${question}`;
  }
  if (intent === 'humor') {
    if (/poop|toilet|bathroom/i.test(seed)) return `${choose([
      'Replicators and excrement. At last, a discussion worthy of the finest minds in Starfleet. Are we investigating the menu or the plumbing?',
      'You ask whether waste becomes dinner. A remarkably efficient way to ruin everyone’s appetite. Do you want an engineering hypothesis or a philosophical nightmare?',
      'Matter recycling may be elegant. Explaining it at a dinner party is not. What made you ask?',
    ], seed, turn)}`;
    return `${choose(['I would laugh, but I am saving that privilege for something truly catastrophic.', 'Humor is the only way some people admit a contradiction without panicking.', 'One might call that amusing. I prefer inconveniently accurate.'], seed, turn)} ${question}`;
  }
  if (references.length) {
    const first = references[0];
    return `${opening} I found an archive lead: ${first.title} [${first.row_id}], marked ${first.verification_status}${first.source_group ? ` in ${first.source_group}` : ''}. ${references.length > 1 ? `${references.length - 1} additional related row(s) are attached.` : ''} A lead is not a verified claim about canon. ${question}`;
  }
  if (intent === 'archive') {
    return `${opening} I cannot attach a matching source-local record to that phrasing. That is a gap in this index, not proof that Star Trek never addressed it. ${view} ${question}`;
  }
  if (intent === 'followup') {
    return `${choose(['I take that as a continuation of our last thought.', 'You are still pulling at the same thread. Sensible.', 'That deserves a closer look, though I would challenge the assumption underneath it.'], seed, turn)} ${view} ${question}`;
  }
  if (topic === 'open') {
    const subject = clean(text.replace(/^(?:could you|can you|would you|please|tell me|what(?:'s| is| are| was| were)|who(?: is| was)|why|how)\b[\s:,.]*/i, '').replace(/[?!.]+$/, ''), 105);
    return `${opening} “${subject || 'That'}” has my attention, although I may need you to tell me more. ${question}`;
  }
  return `${opening} ${view} ${question}`;
}

/** Construct a private, session-only procedural conversation state. */
export function createLoreSemanticEngine({ records = [] } = {}) {
  let archive = [];
  const initialState = () => ({ turnCount: 0, turns: [], lastTopic: null, lastIntent: null, lastReferences: [], visitorFacts: {}, lastVisitorKind: null, firstQuestion: null, supportive: false, repairTarget: null, lastComparison: null, drives: { curiosity: 1, vanity: 0.6, sarcasm: 0.7, contrarianism: 0.5 } });
  let state = initialState();
  function setRecords(nextRecords) {
    const rows = Array.isArray(nextRecords) ? nextRecords : [];
    const used = new Set();
    archive = rows.slice(0, 3000).map(normalizeRecord).filter(row => {
      if (!row || used.has(row.row_id)) return false;
      used.add(row.row_id); return true;
    });
    return archive.length;
  }
  function reset() {
    state = initialState();
  }
  function ask(input) {
    const user = clean(input, 500);
    const topic = topicsFor(user, state);
    const intent = intentFor(user, state);
    if (!state.firstQuestion && /\?/.test(user)) state.firstQuestion = user;
    const techMentioned = TECH_CONCEPTS.filter(concept => concept.pattern.test(user));
    if (techMentioned.length >= 2) state.lastComparison = { labels: techMentioned.slice(0, 2).map(concept => concept.label), turn: state.turnCount };
    if (distressSignal(user) || quietSignal(user)) state.supportive = true;
    else if (/\b(unrelated|new topic|switch topics|let us talk about|let's talk about)\b/i.test(user)) state.supportive = false;
    if (repairSignal(user)) state.repairTarget = [...state.turns].reverse().find(t => !quietSignal(t.user) && !repairSignal(t.user))?.user || state.repairTarget;
    rememberVisitorStatement(user, state);
    const directReply = personalReply(user, state, state.turns.at(-1));
    const explicitTitleRefs = intent === 'source' ? retrieve(archive, user) : [];
    const references = directReply ? [] : intent === 'source' ? (explicitTitleRefs.length ? explicitTitleRefs : [...state.lastReferences]) : intent === 'archive' ? retrieve(archive, user) : [];
    const message = makeText(intent, user, topic, state, references);
    // Session-only memory: recent user turns and links, never saved or transmitted.
    state.turnCount += 1;
    state.turns = [...state.turns, { user, intent, topic, references }].slice(-6);
    state.lastTopic = topic;
    state.lastIntent = intent;
    // Only consecutive archive/source turns may share a citation. Any other
    // conversational turn clears the citation context, so an unrelated topic
    // change cannot manufacture apparent evidence.
    state.lastReferences = (intent === 'archive' || intent === 'source') ? references : [];
    // Mood drives are bounded, observable fiction controls, not mental-state claims.
    state.drives = {
      curiosity: Math.min(1, 0.7 + (state.turnCount % 5) * 0.07),
      vanity: 0.5 + (state.turnCount % 3) * 0.1,
      sarcasm: intent === 'humor' ? 0.9 : 0.65,
      contrarianism: intent === 'boundary' ? 0.95 : 0.5,
    };
    return { text: message, references, intent, topic, mode: LORE_SEMANTIC_MODE };
  }
  function getState() {
    return JSON.parse(JSON.stringify({ ...state, archiveCount: archive.length }));
  }
  setRecords(records);
  return { ask, reset, setRecords, getState };
}
