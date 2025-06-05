package main

import (
    "io"
    "net/http"
    "net/url"
    "github.com/gin-gonic/gin"
)

func main() {
    r := gin.Default()

    r.GET("/fetch", func(c *gin.Context) {
        target := c.Query("url")
        parsed, err := url.Parse(target)
        if err != nil || !(parsed.Scheme == "http" || parsed.Scheme == "https") {
            c.String(400, "Invalid URL")
            return
        }

        resp, err := http.Get(target)
        if err != nil {
            c.String(500, "Fetch failed")
            return
        }
        defer resp.Body.Close()
        body, _ := io.ReadAll(resp.Body)
        c.Data(200, "text/plain", body)
    })

    r.Run(":8080")
}
