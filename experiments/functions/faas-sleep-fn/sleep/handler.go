package function

import (
	"fmt"
	"time"
)

// Handle a serverless request
func Handle(req []byte) string {
	i := 0
	out := ""

	for {
		if i == 10 {
			break
		}

		time.Sleep(1 * time.Second)

		out += fmt.Sprintf("Counter... %d\n", i)

		i++
	}

	out += fmt.Sprintf("\n\nHello, Go. You said: %s", string(req))
	return out
}
