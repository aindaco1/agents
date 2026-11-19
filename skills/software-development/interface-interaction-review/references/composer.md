# Worked example · One message composer

Pablo Stanley's *The life of a composer* explores how small choices accumulate in a message input. Moment 5 revisits the attachment removal control on a phone and during upload. Moment 10, including the Tokyo sequence, explores what Enter means during Japanese text composition. Moment 15 compares ways of handling a follow-up while a reply is in progress. The decisions and proposed checks below are our example handoff for a chat product. [Interactive presentation](https://composer.pablostanley.com/) · [Author's script and numbered outline](https://composer.pablostanley.com/script.js)

## Remove the wrong attachment

**Task.** A person drafting a message notices they attached the wrong file. A remove button revealed on hover keeps the row visually quiet. An always-visible button takes space, but a person using touch can find it before sending. During upload, a spinner can occupy the very spot they need to tap.

**Decision.** Keep a named remove action available by touch and keyboard while the upload is pending. Show progress separately. Removing the file immediately drops it from the draft and returns keyboard focus to the next attachment or, if it was the last, the message field. Discard a late completion for the removed file.

**Proposed check.** With a typed draft and one upload pending, tap Remove on a touch device, finish the upload, then send. The draft text survives removal and the sent message contains no attachment. Repeat using keyboard focus to reach and activate Remove, and check where focus lands.

## Confirm a word before sending

**Task.** The desktop product uses Enter to send a draft. With a Japanese input method active, the same keystroke can accept the highlighted conversion candidate. Binding both actions to that press can send an unfinished sentence.

**Decision.** Give the input method the confirmation keystroke. Keep the confirmed text in the focused draft. A subsequent, separate Enter can use the product's send convention.

**Proposed check.** In a supported desktop browser with a Japanese input method, type a reading, select a conversion candidate, and press Enter once. The converted text remains editable and the conversation has gained zero messages. With composition finished, press Enter again. Exactly one message appears. Use the actual input method when verifying platform behavior.

## Write again while a reply is arriving

**Task.** The person remembers another detail halfway through an answer. Interrupting can suit a correction that invalidates the answer. Holding the draft leaves the person to send it later. In this example the follow-up is additive, and the product can queue one message.

**Decision.** Let the current reply finish. Show a submitted follow-up as queued, with a way to withdraw it before processing begins. Keep Stop distinct so someone who wants to interrupt can do so deliberately.

**Proposed check.** While a reply is arriving, submit the follow-up. The first reply continues and the follow-up is visibly queued. Withdraw it before the first reply finishes. Once the reply ends, only the original message has received an answer. On a second run leave the follow-up queued and check that it starts exactly once after the first reply finishes.
