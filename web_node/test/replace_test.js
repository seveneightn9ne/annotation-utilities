
sent_xml = '#SENT=I was  <ns type="S"><i>shoked</i><c>shocked</c></ns> because I had  <ns type="S"><i>alredy</i><c>already</c></ns> spoken with them and I had  <ns type="RV"><i>taken</i><c>got</c></ns> two autographs.';
sent_xml = sent_xml.replace('type="', 'class="error ');

console.log(sent_xml);