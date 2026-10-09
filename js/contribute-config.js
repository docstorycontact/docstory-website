/**
 * DocStory — Contributor program settings (js/contribute-config.js)
 * Every page in /contribute/ reads these, so a change here updates the whole program.
 */
window.DOCSTORY_CONTRIBUTE = {
  payEnabled: true,
  payAmount: 50,            // dollars per verified, published interview
  paidCap: 5,               // schools with this many published interviews or more are no longer paid
  payMethods: 'PayPal or Venmo',

  // Web3Forms access key. It's meant to be public (it only lets people send TO your inbox).
  // Submissions are emailed to the address you signed up to Web3Forms with.
  web3formsKey: '0f6bf157-5949-423d-b2c2-22b4aba34487',

  // The address you'll send verification emails from. Shown to contributors so they know
  // which emails are really from DocStory. Leave empty to show "a DocStory email address".
  contactEmail: 'docstory.contact@gmail.com',

  reviewDays: 7,            // we email the contributor within this many days of submission
  replyDays: 14,            // they have this long to verify and approve
  payDays: 7,               // payment goes out within this many days of publication
};
