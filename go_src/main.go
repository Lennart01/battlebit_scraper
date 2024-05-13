package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"time"

	influxdb2 "github.com/influxdata/influxdb-client-go/v2"
	"github.com/influxdata/influxdb-client-go/v2/api"
	"github.com/joho/godotenv"
)

type Server struct {
	Map          string `json:"Map"`
	MapSize      string `json:"MapSize"`
	Gamemode     string `json:"Gamemode"`
	Region       string `json:"Region"`
	Players      int    `json:"Players"`
	QueuePlayers int    `json:"QueuePlayers"`
	MaxPlayers   int    `json:"MaxPlayers"`
	Hz           int    `json:"Hz"`
	DayNight     string `json:"DayNight"`
	IsOfficial   bool   `json:"IsOfficial"`
	HasPassword  bool   `json:"HasPassword"`
	AntiCheat    string `json:"AntiCheat"`
	Build        string `json:"Build"`
}

func initInfluxDB() (influxdb2.Client, api.WriteAPI) {
	err := godotenv.Load()
	if err != nil {
		fmt.Println("No .env file found, proceeding with environment variables")
	}

	token := os.Getenv("INFLUXDB_TOKEN")
	org := os.Getenv("INFLUXDB_ORG")
	url := os.Getenv("INFLUXDB_URL")
	bucket := os.Getenv("INFLUXDB_BUCKET")

	client := influxdb2.NewClient(url, token)
	writeAPI := client.WriteAPI(org, bucket)

	return client, writeAPI
}

func writeData(servers []Server, writeAPI api.WriteAPI) {
	timestamp := time.Now()

	// Aggregated statistics
	stats := map[string]map[string]int{
		"Map":         {},
		"MapSize":     {},
		"Gamemode":    {},
		"Region":      {},
		"MaxPlayers":  {},
		"Hz":          {},
		"DayNight":    {},
		"IsOfficial":  {},
		"HasPassword": {},
		"AntiCheat":   {},
		"Build":       {},
	}

	// Count occurrences of each stat
	for _, server := range servers {
		stats["Map"][server.Map]++
		stats["MapSize"][server.MapSize]++
		stats["Gamemode"][server.Gamemode]++
		stats["Region"][server.Region]++
		stats["MaxPlayers"][fmt.Sprint(server.MaxPlayers)]++
		stats["Hz"][fmt.Sprint(server.Hz)]++
		stats["DayNight"][server.DayNight]++
		stats["IsOfficial"][fmt.Sprintf("%t", server.IsOfficial)]++
		stats["HasPassword"][fmt.Sprintf("%t", server.HasPassword)]++
		stats["AntiCheat"][server.AntiCheat]++
		stats["Build"][server.Build]++
	}

	// Write the stats to InfluxDB
	for stat, counts := range stats {
		for value, count := range counts {
			p := influxdb2.NewPointWithMeasurement(stat+"_stats").
				AddTag(stat, value).
				AddField("count", count).
				SetTime(timestamp)
			writeAPI.WritePoint(p)
		}
	}

	// Write total server count
	serverCountPoint := influxdb2.NewPointWithMeasurement("server_count").
		AddField("count", len(servers)).
		SetTime(timestamp)
	writeAPI.WritePoint(serverCountPoint)

	fmt.Printf("Wrote aggregated data to InfluxDB\n")
}

func getData() ([]Server, error) {
	url := "https://publicapi.battlebit.cloud/Servers/GetServerList"
	resp, err := http.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("unexpected status code: %d", resp.StatusCode)
	}
	bodyBytes, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		log.Println("Error reading response body:", err)
		return nil, err
	}

	bom := []byte{0xEF, 0xBB, 0xBF}
	bodyBytes = bytes.TrimPrefix(bodyBytes, bom)

	var servers []Server
	err = json.Unmarshal(bodyBytes, &servers)
	if err != nil {
		log.Println("Error decoding JSON:", err)
		return nil, err
	}

	return servers, nil
}

func main() {
	client, writeAPI := initInfluxDB()
	defer client.Close()

	for {
		servers, err := getData()
		if err != nil {
			fmt.Println("Error fetching data:", err)
			time.Sleep(15 * time.Second)
			continue
		}

		writeData(servers, writeAPI)

		// Flush writes
		writeAPI.Flush()

		time.Sleep(15 * time.Second)
	}
}
