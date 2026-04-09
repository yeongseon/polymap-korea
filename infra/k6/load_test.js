import http from "k6/http";
import { check, sleep } from "k6";

const baseUrl = __ENV.K6_BASE_URL || "http://localhost:8000";

export const options = {
  stages: [
    { duration: "30s", target: 10 },
    { duration: "1m", target: 10 },
    { duration: "30s", target: 0 },
  ],
  thresholds: {
    http_req_duration: ["p(95)<500"],
    http_req_failed: ["rate<0.01"],
  },
};

const endpoints = [
  "/api/v1/health",
  "/api/v1/elections",
  "/api/v1/issues",
  "/api/v1/search?q=%EA%B5%90%EC%9C%A1",
];

export default function () {
  for (const endpoint of endpoints) {
    const response = http.get(`${baseUrl}${endpoint}`);
    check(response, {
      [`${endpoint} returned 200`]: (res) => res.status === 200,
    });
  }

  sleep(1);
}
