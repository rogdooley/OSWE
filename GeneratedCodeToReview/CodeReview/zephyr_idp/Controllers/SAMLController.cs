using System.Web.Mvc;
using System.Xml;

namespace ZephyrIDP.Controllers
{
    public class SAMLController : Controller
    {
        [HttpPost]
        public ActionResult ACS()
        {
            string samlResponse = Request.Form["SAMLResponse"];
            byte[] data = System.Convert.FromBase64String(samlResponse);
            string decoded = System.Text.Encoding.UTF8.GetString(data);

            XmlDocument xmlDoc = new XmlDocument();
            xmlDoc.PreserveWhitespace = true;
            xmlDoc.LoadXml(decoded);

            XmlNamespaceManager ns = new XmlNamespaceManager(xmlDoc.NameTable);
            ns.AddNamespace("saml", "urn:oasis:names:tc:SAML:2.0:assertion");

            var nameIdNode = xmlDoc.SelectSingleNode("//saml:NameID", ns);
            var name = nameIdNode?.InnerText ?? "Unknown";

            return Content("Authenticated: " + name);
        }
    }
}
