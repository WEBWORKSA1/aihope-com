/* AI Hope site settings: the only script you normally need to edit. */
window.AIH_CONFIG = {
  /* Forms are delivered by FormSubmit (free, no backend). The inbox is never written in the
     page source: it is rebuilt from this encoded array only at the moment a form is sent.
     After the first submission, FormSubmit emails an activation link plus a random-string
     alias. Paste that alias into formAlias to stop using the encoded inbox at all. */
  formEndpoint: "https://formsubmit.co/ajax/",
  formAlias: "",
  _k: [120, 122, 110, 57, 119, 116, 108, 120, 114, 75, 60, 108, 126, 118, 125, 122, 130, 109, 112, 130],

  /* Google AdSense. Auto ads run from the <head> code on every page. To place fixed units in
     the reserved spots, create display units in AdSense and paste their slot ids here. */
  adsense: { client: "ca-pub-6620975821265271", slots: { "in-article": "", "sidebar": "", "in-feed": "" } },

  /* Donations: paste payment links (Stripe Payment Links, PayPal, Buy Me a Coffee, GitHub Sponsors…).
     While both are empty, the support page collects a pledge and the team follows up with a secure link. */
  donate: { oneTime: "", monthly: "", currency: "USD" },

  youtubeChannel: "",   /* e.g. https://www.youtube.com/@aihope */
  ga4: ""               /* e.g. G-XXXXXXXXXX */
};
