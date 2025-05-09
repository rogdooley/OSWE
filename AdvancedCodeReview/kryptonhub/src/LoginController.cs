using Microsoft.AspNetCore.Mvc;
using System.Data.SqlClient;

namespace KryptonHub.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class LoginController : ControllerBase
    {
        [HttpPost]
        public string Login([FromForm] string username, [FromForm] string password)
        {
            string connStr = "Server=localhost;Database=Krypton;User Id=sa;Password=yourStrong(!)Password;";
            using var conn = new SqlConnection(connStr);
            conn.Open();
            var cmd = conn.CreateCommand();
            cmd.CommandText = $"SELECT role FROM users WHERE user='{username}' AND pass='{password}'";
            var role = cmd.ExecuteScalar();
            return role != null ? $"Logged in as {role}" : "Invalid credentials";
        }
    }
}
