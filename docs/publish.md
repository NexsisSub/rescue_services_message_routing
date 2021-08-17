`POST` sur `http://127.0.0.1:8888/publish` 
avec un objet XML CISU ou EMSI

Ou avec CURL :
```bash
curl --location --request POST 'http://127.0.0.1:8888/publish' \
--header 'Content-Type: application/xml' \
--data-raw '<?xml version="1.0" encoding="UTF-8"?>
<edxlDistribution xlink:type="extended"
                  xmlns="urn:oasis:names:tc:emergency:EDXL:DE:2.0"
                  xmlns:xlink="http://www.w3.org/1999/xlink"
                  xmlns:ct="urn:oasis:names:tc:emergency:edxl:ct:1.0">
  <distributionID>8e80536c-b5b3-4653-9f9d-3c5e0b3c9fd0</distributionID>
  <senderID>sga-nexsis</senderID>
  <dateTimeSent>2021-06-24T13:50:40+00:00</dateTimeSent>
  <dateTimeExpires>2071-06-24T13:50:40+00:00</dateTimeExpires>
  <distributionStatus>Actual</distributionStatus>
  <distributionKind>Report</distributionKind>
  <descriptor xlink:type="resource">
    <language>fr-FR</language>
    <explicitAddress>
      <explicitAddressScheme>sge</explicitAddressScheme>
      <explicitAddressValue>sgo-samu-77</explicitAddressValue>
    </explicitAddress>
  </descriptor>
  <content xlink:type="resource">
    <contentObject xlink:type="resource">
      <contentXML>
        <embeddedXMLContent>
            <message xmlns="urn:emergency:cisu:2.0">
    <messageId>8e80536c-b5b3-4653-9f9d-3c5e0b3c9fd0</messageId>
    <sender>
      <name>sga-nexsis</name>
      <URI>sge:sga-nexsis</URI>
    </sender>
    <sentAt>2021-06-24T13:50:40+00:00</sentAt>
    <msgType>ALERT</msgType>
    <status>ACTUAL</status>
    <recipients>
        <recipient>
          <name>pompiers-77</name>
          <URI>sge:77-cgo</URI>
        </recipient>
        <recipient>
          <name>police-77</name>
          <URI>sge:sgo-police-77</URI>
        </recipient>
        <recipient>
          <name>bon-samaritain-77</name>
          <URI>sge:sgo-bon-samaritain</URI>
        </recipient>
        <recipient>
          <name>samu-77</name>
          <URI>sge:sgo-samu-77</URI>
        </recipient>
    </recipients>
    <createEvent>
      <eventId>fcb6fb07-fde0-453a-89c6-e0aef28213c3</eventId>
      <createdAt>2021-06-24T13:50:39+00:00</createdAt>
      <severity>SEVERE</severity>
        <eventLocation>
            <loc_Id>111fb03a-6fd9-41e0-8e81-990c45188888</loc_Id>
            <type>POINT</type>
            <coordsys>EPSG:4326</coordsys>
            <height_role>AVE</height_role>
          <coord>
            <lat>48.549675</lat>
            <lon>2.646865</lon>
          </coord>
            <address>Avenue Marc Jacquet</address>
            <address>Melun</address>
            <address>(77288)</address>
        </eventLocation>
        <primaryAlert>
          <alertId>632dc179-98ea-49fa-a574-18e67be2748d</alertId>
          <receivedAt>2021-06-24T13:50:14+00:00</receivedAt>
          <reporting>STANDARD</reporting>
            <alertLocation>
                <type>POINT</type>
                <coordsys>EPSG:4326</coordsys>
              <coord>
                <lat>48.549675</lat>
                <lon>2.646865</lon>
              </coord>
                <address>Avenue Marc Jacquet</address>
                <address>Melun</address>
                <address>(77288)</address>
            </alertLocation>
            <call>
                <source>requérant</source>
                <dialledURI>tel:undefined</dialledURI>
            </call>
          <caller>
            <callerURI>manual</callerURI>
          </caller>
            <callTaker></callTaker>
          <alertCode>
            <version>latest</version>
            <whatsHappen>
              <code>C01.02.00</code>
              <label>Accident de la circulation|Accident ferroviaire</label>
            </whatsHappen>
              <locationKind>
                <code>L02.01.00</code>
                <label>Circulation/transport|Voie publique hors voie rapide</label>
              </locationKind>
              <healthMotive>
                <code>M01.01</code>
                <label>Détresse vitale|Suspicion d’arrêt cardiaque, mort subite</label>
              </healthMotive>
            <victims>
                <count>1</count>
            </victims>
          </alertCode>
        </primaryAlert>
    </createEvent>
  </message>
        </embeddedXMLContent>
      </contentXML>
    </contentObject>
  </content>
</edxlDistribution>'
```