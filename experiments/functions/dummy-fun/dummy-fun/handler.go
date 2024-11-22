package function

import (
	"fmt"
	"math/rand"
	"os"
	"strconv"
	"time"
)

const (
	ENV_LOOPS_FOR_TIME_UNIT    = "DUMMY_FUN_LOOPS_FOR_TIME_UNIT"
	ENV_EXPONENTIAL_DURATION   = "DUMMY_FUN_EXPONENTIAL_DURATION"
	ENV_SERVICE_RATE_MI        = "DUMMY_FUN_SERVICE_RATE_MI"
	ENV_OUTPUT_PAYLOAD_ENABLED = "DUMMY_FUN_OUTPUT_PAYLOAD_ENABLED"
	ENV_OUTPUT_PAYLOAD_KB      = "DUMMY_FUN_OUTPUT_PAYLOAD_KB"
)

var looping = true

// Handle a serverless request
func Handle(req []byte) string {
	s1 := rand.NewSource(time.Now().UnixNano())
	r1 := rand.New(s1)

	mi, _ := strconv.ParseFloat(os.Getenv(ENV_SERVICE_RATE_MI), 1.0)
	loopsForTimeUnit, err := strconv.ParseInt(os.Getenv(ENV_LOOPS_FOR_TIME_UNIT), 10, 64)
	if err != nil {
		loopsForTimeUnit = 25000000
	}

	exponentialAlfa, _ := strconv.ParseBool(os.Getenv(ENV_EXPONENTIAL_DURATION))
	var alfa float64
	if exponentialAlfa {
		alfa = r1.ExpFloat64() / mi
	} else {
		alfa = mi
	}

	actualLoops := int(float64(loopsForTimeUnit) * alfa)

	startTime := time.Now()

	// start dummy loop
	for i := 0; i < actualLoops; i++ {
		r1.Float64()
	}
	elapsed := time.Since(startTime)

	// create the output payload
	// outputPayloadEnabled, _ := strconv.ParseBool(os.Getenv(ENV_OUTPUT_PAYLOAD_ENABLED))
	// if outputPayloadEnabled {
	//	outputPayloadKb, _ := strconv.ParseInt(os.Getenv(ENV_OUTPUT_PAYLOAD_KB))

	//	var b bytes.Buffer
	//	buf = bufio.NewWriter(&b)
	// }

	return fmt.Sprintf("loops for time unit = %d\nloops = %d\nmi = %.2f\nalfa = %.2f\nelapsed time = %.4f",
		loopsForTimeUnit, actualLoops, mi, alfa, elapsed.Seconds())
}

/*

// Use the following handler to understand how many loops are needed
func Handle(req []byte) string {
	s1 := rand.NewSource(time.Now().UnixNano())
	r1 := rand.New(s1)

	mi, _ := strconv.ParseFloat(os.Getenv("mi"), 1.0)
	alfa := r1.ExpFloat64() / mi
	alfa = 1.0

	milliseconds := time.Duration(alfa * 1000)

	timer := time.NewTimer(milliseconds * time.Millisecond)
	go func() {
		<-timer.C
		looping = false
	}()

	i := 0
	startTime := time.Now()

	// test loop time
	for {
		i++
		if !looping {
			break
		}
		rand.Float64()
	}
	elapsed := time.Since(startTime)

	return fmt.Sprintf("loops = %d\nmi = %.2f\nalfa = %.2f\nelapsed time = %.4f", i, mi, v, elapsed.Seconds())
}

*/
