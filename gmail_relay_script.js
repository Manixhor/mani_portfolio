function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    GmailApp.sendEmail(data.to, data.subject, data.body, {
      from: data.from || 'manigururam08@gmail.com',
      name: data.name || 'Portfolio'
    });
    return ContentService.createTextOutput(JSON.stringify({success: true}));
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({success: false, error: err.message}));
  }
}
