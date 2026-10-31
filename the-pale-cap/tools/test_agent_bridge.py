import io
import json
import unittest
from unittest.mock import patch

from agent_bridge import Decision, decide, COMMANDS


class AgentBridgeTests(unittest.TestCase):
    def test_schema_rejects_world_mutations_and_unknown_intents(self):
        for value in [
            {"command": "teleport", "speech": "Hi"},
            {"command": "follow", "speech": "Hi", "bag": 99},
            {"command": "follow", "speech": "x" * 241},
        ]:
            with self.assertRaises(ValueError):
                Decision.parse(json.dumps(value))

    def test_offline_never_calls_network(self):
        with patch("urllib.request.urlopen") as request:
            self.assertEqual(decide({"joined": 1}, "wait").command, "wait")
            self.assertEqual(decide({"joined": 0}, "a request").command, "forage")
            request.assert_not_called()

    def test_typed_tool_choice_retry_and_bounded_fallback(self):
        def response(command):
            return io.StringIO(
                json.dumps(
                    {
                        "choices": [
                            {
                                "message": {
                                    "tool_calls": [
                                        {
                                            "function": {
                                                "name": "choose_intent",
                                                "arguments": json.dumps(
                                                    {"command": command, "speech": "Coming."}
                                                ),
                                            }
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                )
            )

        with patch.dict("os.environ", {"XAI_API_KEY": "unit-test-placeholder"}):
            with patch(
                "urllib.request.urlopen", side_effect=[response("teleport"), response("follow")]
            ) as request:
                decision = decide({"joined": 1}, "Stay close", run=True)
                self.assertEqual(decision.command, "follow")
                payload = json.loads(request.call_args[0][0].data)
                self.assertTrue(payload["tools"][0]["function"]["strict"])
                self.assertEqual(payload["tool_choice"]["function"]["name"], "choose_intent")
                self.assertEqual(request.call_count, 2)
            with patch(
                "urllib.request.urlopen", side_effect=[response("teleport"), response("teleport")]
            ) as request:
                decision = decide({"joined": 0}, "Invent gold", run=True)
                self.assertIn("[Offline]", decision.speech)
                self.assertEqual(request.call_count, 2)
        self.assertNotIn("give", COMMANDS)
