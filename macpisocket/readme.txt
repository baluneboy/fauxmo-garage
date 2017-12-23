Typical
1. K: Alexa, turn on the garage.
2. A: Okay.
3. R: GPIO push garage remote button, and turn off torch.

New (R is client, M is server)
1. K: Alexa, turn on the garage.
2. A: Okay.
3. R: Request to M (server) "is it open?".
4. M: Snap picture.
5. M: Analyze image.
6. M: Send reply to R (client): "seems:open".
7. R: Get reply from server, if trigger action comes back True, then do it.
8. R: Wait for timer amt (delta for door to open or close).
9. Now repeat steps 3 - 8 (once, maybe twice).

Darknet (R is client, M is server) to just do query if open (flash indicator light, make sound)
1. K: Alexa, turn on the darknet.
2. A: Okay.
3. R: Request to M (server) "is it open?".
4. M: Snap picture.
5. M: Analyze image.
6. M: Send reply to R (client): "seems:open,median:VALUE".
7. R: Speak results, flash lights, play victory or defeat sound.

WHAT ABOUT SMALLER TEMPLATE (JUST CIRCLE STRUCTURE)?

WHAT ABOUT A SNOW TEMPLATE?