using Microsoft.AspNetCore.Mvc;
using System.Collections.Concurrent;

namespace IronPass.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class ResetController : ControllerBase
    {
        private static ConcurrentDictionary<string, string> tokens = new ConcurrentDictionary<string, string>();

        [HttpPost("request")]
        public IActionResult RequestReset([FromQuery] string email)
        {
            string token = System.Guid.NewGuid().ToString();
            tokens[email] = token;
            return Ok(new { message = "Reset link sent", token = token });
        }

        [HttpPost("submit")]
        public IActionResult SubmitReset([FromQuery] string email, [FromQuery] string token, [FromQuery] string newpass)
        {
            if (tokens.TryGetValue(email, out string validToken) && validToken == token)
            {
                tokens[email] = null; // expire token
                return Ok(new { message = "Password reset for " + email });
            }
            return BadRequest("Invalid token.");
        }
    }
}
