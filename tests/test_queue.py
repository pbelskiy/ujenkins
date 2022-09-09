import re

import responses

QUEUE_JSON = """
{
  "_class" : "hudson.model.Queue",
  "discoverableItems" : [

  ],
  "items" : [
    {
      "_class" : "hudson.model.Queue$BlockedItem",
      "actions" : [
        {
          "_class" : "hudson.model.CauseAction",
          "causes" : [
            {
              "_class" : "hudson.model.Cause$UserIdCause",
              "shortDescription" : "Started by user admin",
              "userId" : "admin",
              "userName" : "admin"
            }
          ]
        }
      ],
      "blocked" : true,
      "buildable" : false,
      "id" : 14,
      "inQueueSince" : 1662756642196,
      "params" : "",
      "stuck" : false,
      "task" : {
        "_class" : "hudson.model.FreeStyleProject",
        "name" : "test",
        "url" : "http://localhost:8080/job/test/",
        "color" : "blue_anime"
      },
      "url" : "queue/item/14/",
      "why" : "Build #8 is already in progress (ETA: 1 min 33 sec)",
      "buildableStartMilliseconds" : 1662756642197
    }
  ]
}
"""


@responses.activate
def test_get(client):
    responses.add(
        responses.GET,
        re.compile(r'.+/queue/api/json'),
        content_type='application/json;charset=utf-8',
        body=QUEUE_JSON
    )

    queue = client.queue.get()
    assert len(queue) == 1
