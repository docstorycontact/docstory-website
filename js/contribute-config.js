/**
 * DocStory — Contributor program settings (js/contribute-config.js)
 * Every page in /contribute/ reads these, so a change here updates the whole program.
 */
window.DOCSTORY_CONTRIBUTE = {
  // The single on/off switch for paying contributors. After changing it, rebuild so every page matches:
  //   python3 build.py && python3 build_schools.py
  // Off = volunteer mode: no "Get Paid!" pill, no amounts, volunteer wording and link preview.
  payEnabled: true,
  payAmount: 20,            // dollars per verified, published interview
  paidCap: 5,               // schools with this many published interviews or more are no longer paid
  payMethods: 'PayPal, Venmo, or an Amazon.com eGift card',

  // Referral thank-yous, paid to a published contributor for each person they refer whose interview
  // is published. Weighted toward schools DocStory doesn't cover yet, so referrals spread across
  // schools instead of piling up at one. Off whenever payEnabled is off. Rebuild after changing.
  referralNewSchool: 15,    // the referred person's school had no published interviews
  referralOpenSchool: 5,    // it had some, but fewer than paidCap (no thank-you at paidCap or more)

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
