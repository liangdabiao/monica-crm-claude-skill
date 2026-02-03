# Monica API Documentation

> Source: https://www.monicahq.com/api

## Table of Contents

1. [Overview](#overview)
2. [Current Version](#current-version)
3. [Schema](#schema)
4. [HTTP Verbs](#http-verbs)
5. [Client Errors](#client-errors)
6. [Authentication](#authentication)
7. [Pagination](#pagination)
8. [Rate Limiting](#rate-limiting)
9. [API Endpoints](#api-endpoints)
   - [Contacts](#contacts)
   - [Notes](#notes)
   - [Activities](#activities)
   - [Reminders](#reminders)
   - [Tasks](#tasks)
   - [Tags](#tags)

---

## Overview

This document describes how to use Monica's API. This document is heavily inspired by GitHub's and Stripe's API. Please use the API in a nice way and don't be a jerk.

## Current Version

By default, all requests to `https://app.monicahq.com/api` receive the v1 version of the API.

## Schema

All API access is over HTTPS, and accessed from the `https://app.monicahq.com/api` URL. All data is sent and received as JSON.

If you do have a custom instance of Monica, replace the URL above with the URL of your instance. The endpoint will always be `YOUR_URL/api`.

### Response Headers

```
Server: nginx/1.11.9
Content-Type: application/json
Transfer-Encoding: chunked
Connection: keep-alive
Cache-Control: no-cache, private
Date: Thu, 14 Sep 2017 02:24:19 GMT
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 58
```

### Timestamps

All timestamps return in ISO 8601 format: `YYYY-MM-DDTHH:MM:SSZ`

### Summary Representations

When you fetch a list of resources, for instance the list of reminders, you will always get a subset of a contact attached to it, giving you just enough information so you don't need to fetch the full information of the contact to do something with it.

## HTTP Verbs

Monica tries to use the appropriate HTTP verbs wherever it can. Note that the `PATCH` HTTP verb is not used right now.

| Verb | Description |
| --- | --- |
| GET | Used for retrieving resources. |
| POST | Used for creating resources. |
| PUT | Used for replacing resources or collections. |
| DELETE | Used for deleting resources. |

## Client Errors

### Invalid JSON

Sending an invalid JSON during a POST or a PUT will result in an error.

```json
{
  "error": {
    "message": "Problems parsing JSON",
    "error_code": 37
  }
}
```

### All Custom Errors

| Code | Message | Explanation |
| --- | --- | --- |
| 30 | The limit parameter is too big. | The maximum number for the limit parameter in a request is 100. |
| 31 | The resource has not been found. | Comes along with a 404 HTTP error code. |
| 32 | Error while trying to save the data. | Happens when the validation (during a `POST` or `PUT`) fails for some reason. |
| 33 | Too many parameters. | Happens when we try to save the data from the JSON, but the object expected different parameters. |
| 34 | Too many attempts, please slow down the request. | You are limited to 60 API calls per minute. |
| 35 | This email address is already taken. | An email address should be unique in the account. |
| 36 | You can't set a partner or a child to a partial contact. | |
| 37 | Problems parsing JSON. | When doing a `PUT` or `POST`, returns an error if the JSON is not a valid JSON or badly formatted. |
| 38 | Date should be in the future. | When setting up a reminder, the date should be in the future. |
| 39 | The sorting criteria is invalid. | Sorting query only allows a few criterion. |
| 40 | Invalid query. | The query is invalid for obscure reasons. It might be an invalid method call, an invalid sorting criteria, or something else. This should not happen often. |
| 41 | Invalid parameters. | Parameters in the JSON request are invalid. |

## Authentication

There are several ways to authenticate to the API. All requests to the API require authentication.

### OAuth 2 Token (sent in a header)

```bash
curl -H "Authorization: Bearer OAUTH-TOKEN" https://app.monicahq.com/api
```

### OAuth2 Key/Secret

This is meant to be used in server to server scenarios. Never reveal your OAuth application's client secret to your users. To use this authentication method, you need to first register an application in your Monica's instance.

## Pagination

Requests that return multiple items will be paginated to 10 items by default. You can specify further pages with the `?page` parameter. For some resources, you can also set a custom page size up to 100 with the `?limit` parameter. Omitting the `?page` parameter will return the first page.

```bash
curl 'https://app.monicahq.com/api/contacts?page=2&limit=100'
```

## Rate Limiting

The returned HTTP headers of any API request show your current rate limit status:

```
Date: Thu, 14 Sep 2017 02:24:19 GMT
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 58
```

| Header name | Description |
| --- | --- |
| X-RateLimit-Limit | The maximum number of requests you're permitted to make per minute. |
| X-RateLimit-Remaining | The number of requests remaining in the current rate limit window. |

If you exceed the rate limit, a `429` error response returns with a JSON:

```
X-RateLimit-Limit   60
X-RateLimit-Remaining   0
Retry-After 55
```

```json
{
    "error": {
        "message": "Too many attempts, please slow down the request.",
        "error_code": 34
    }
}
```

---

# API Endpoints

## Contacts

### Overview

The Contact object is the core of what Monica is all about. The API allows you to create, delete and update your contacts. You can retrieve individual contacts as well as a list of all your contacts.

It's important to understand that all the people in Monica are Contact objects - that includes relationship contacts like kids or significant other. However, there are two types of contacts:

- `real` contacts
- `partial` contacts.

A `real` contact is a contact that you have a lot of information about - therefore you can attach activities, reminders, notes, etc... to the object. Real contacts have their own contact sheet.

A `partial` contact, however, is a person you don't have a lot of information about. This is typically the spouse of one of your friend, or their child for whom you only need to remember the names and the date of birth. A `partial` contact is always linked to a `real` contact. Partial contacts don't have their own contact sheet and shouldn't have one.

A `partial` contact has the flag `is_partial` set to `true`.

When creating `real` contacts, the only rule is the uniqueness of the email address in the user's account. If you try to use the same email address when creating another contact in the account, the API will return an error.

#### Special Dates

Some dates about a contact are considered "special". Currently three dates have this special type:

- birthdate
- deceased date
- first met date

Those dates are special because they can be based on different factors:

- User knows the exact date: Oct 29 1981.
- User knows only the month and day, but not the year: Oct 29.
- User knows the age, but not the date.
- User doesn't know the date at all.

When you retrieve one of these dates, here is what you get:

```json
{
"birthdate": {
  "is_age_based": false,
  "is_year_unknown": false,
  "date": "1994-01-27T00:00:00Z"
}
```

- If the `date` field is present and not null, that means we know a date for the birthdate of the contact.
- `is_age_based`: this indicates whether the date is based on the age provided by the user or not. When it is, `date` is set with the right year, but the month and the day should be set to `01`. We can't set a reminder to a date that is age-based.
- `is_year_unknown`: this indicates whether we know the year of birth of the contact or not. If we don't know the year, `date` has to be set to the current year.

Note that `is_year_unknown` and `is_age_based` are mutually exclusive. That means, if `is_age_based` is true, `is_year_unknown` has to be false and vice versa.

Below is a summary of the different use-cases. We assume the current year is 2017.

**I don't know the date of birth of a contact**

Query:
```json
{
...
"birthdate": null,
"birthdate_is_age_based": false,
"birthdate_is_year_unknown": false,
"birthdate_age": null,
...
```

Response:
```json
{
"birthdate": {
  "is_age_based": false,
  "is_year_unknown": false,
  "date": null
}
```

**I only know the age of a contact**

Query:
```json
{
...
"birthdate": null,
"birthdate_is_age_based": true,
"birthdate_is_year_unknown": false,
"birthdate_age": 29,
...
```

Response:
```json
{
"birthdate": {
  "is_age_based": true,
  "is_year_unknown": false,
  "date": "1994-01-01T00:00:00Z"
}
```

**I know the day and month of birth of a contact**

Query:
```json
{
...
"birthdate": "2017-10-29 00:00:00",
"birthdate_is_age_based": false,
"birthdate_is_year_unknown": true,
"birthdate_age": null,
...
```

Response:
```json
{
"birthdate": {
  "is_age_based": false,
  "is_year_unknown": true,
  "date": "2017-10-29T00:00:00Z"
}
```

**I know the day, month and year of birth of a contact**

Query:
```json
{
...
"birthdate": "1994-03-21 00:00:00",
"birthdate_is_age_based": false,
"birthdate_is_year_unknown": false,
"birthdate_age": null,
...
```

Response:
```json
{
"birthdate": {
  "is_age_based": false,
  "is_year_unknown": false,
  "date": "1994-03-21T00:00:00Z"
}
```

### List all your contacts

**GET** `/contacts/`

#### Parameters

| Name | Type | Description |
| --- | --- | --- |
| limit | integer | Indicates the page size. |
| page | integer | Indicates the page to return. |
| query | string | Performs a search with the given query. |
| sort | string | Indicates how the query should be ordered by. Possible values: `created_at`, `-created_at`, `updated_at`, `-updated_at`. |

#### Response

```json
{
  "data": [
    {
      "id": 1,
      "object": "contact",
      "first_name": "Justen",
      "last_name": "Flatley",
      "nickname": "Rambo",
      "gender": "male",
      "is_partial": false,
      "is_dead": false,
      "last_called": null,
      "last_activity_together": {
        "date": "1977-07-17 00:00:00.000000",
        "timezone_type": 3,
        "timezone": "US\/Eastern"
      },
      "stay_in_touch_frequency": 5,
      "stay_in_touch_trigger_date": "2018-04-26T09:25:43Z",
      "information": {
        "relationships": {
          "love": {
            "total": 0,
            "contacts": []
          },
          "family": {
            "total": 1,
            "contacts": [
              {
                "relationship": {
                  "id": 1,
                  "name": "son",
                },
                "contact": {
                  "id": 2,
                  "object": "contact",
                  "first_name": "Oscar",
                  "last_name": "Tremblay",
                  "nickname": "Rambo",
                  "gender": "male",
                  "is_partial": true,
                  "information": {
                    "birthdate": {
                      "is_age_based": false,
                      "is_year_unknown": true,
                      "date": "2017-11-29T00:00:00Z"
                    }
                  },
                  "account": {
                    "id": 1
                  }
                }
              }
            ]
          },
          "friend": {
            "total": 1,
            "contacts": [
              {
                "relationship": {
                  "id": 1,
                  "name": "son",
                },
                "contact": {
                  "id": 3,
                  "object": "contact",
                  "first_name": "Makayla",
                  "last_name": null,
                  "nickname": "Rambo",
                  "gender": "female",
                  "is_partial": false,
                  "information": {
                    "birthdate": {
                      "is_age_based": false,
                      "is_year_unknown": true,
                      "date": "2017-02-27T00:00:00Z"
                    }
                  },
                  "account": {
                    "id": 1
                  }
                }
              }
            ]
          },
          "work": {
            "total": 0,
            "contacts": []
          }
        },
        "dates": {
          "birthdate": {
            "is_age_based": null,
            "is_year_unknown": null,
            "date": null
          },
          "deceased_date": {
            "is_age_based": null,
            "is_year_unknown": null,
            "date": null
          }
        },
        "career": {
          "job": null,
          "company": null
        },
        "avatar": {
          "url": "https:\/\/randomuser.me\/api\/portraits\/men\/39.jpg",
          "source": "external"
        },
        "food_preferencies": "Alice was a paper label, with the distant sobs of the March Hare. Visit either you like: they're both mad.' 'But I don't believe you do lessons?' said Alice, 'because I'm not myself, you see.' 'I.",
        "how_you_met": {
          "general_information": "King exclaimed.",
          "first_met_date": {
            "is_age_based": null,
            "is_year_unknown": null,
            "date": null
          },
          "first_met_through_contact": {
            "id": 4,
            "object": "contact",
            "first_name": "Johnathon",
            "last_name": "Stark",
            "nickname": "Rambo",
            "gender": "male",
            "is_partial": true,
            "is_dead": false,
            "information": {
              "birthdate": {
                "is_age_based": false,
                "is_year_unknown": true,
                "date": "2017-09-24T00:00:00Z"
              },
              "deceased_date": {
                "is_age_based": null,
                "is_year_unknown": null,
                "date": null
              }
            },
            "account": {
              "id": 1
            }
          }
        }
      },
      "addresses": [],
      "tags": [],
      "statistics": {
        "number_of_calls": 0,
        "number_of_notes": 5,
        "number_of_activities": 3,
        "number_of_reminders": 0,
        "number_of_tasks": 3,
        "number_of_gifts": 7,
        "number_of_debts": 1
      },
      "account": {
        "id": 1
      },
      "created_at": "2017-12-12T09:57:15Z",
      "updated_at": "2017-12-12T09:57:15Z"
    }
  ],
  "links": {
    "first": "http:\/\/monica.app\/api\/contacts?page=1",
    "last": "http:\/\/monica.app\/api\/contacts?page=104",
    "prev": null,
    "next": "http:\/\/monica.app\/api\/contacts?page=2"
  },
  "meta": {
    "current_page": 1,
    "from": 1,
    "last_page": 104,
    "path": "http:\/\/monica.app\/api\/contacts",
    "per_page": "2",
    "to": 2,
    "total": 208
  }
}
```

#### Sorting

You can sort this query. Accepted criteria are:

| Name | Description |
| --- | --- |
| `created_at` | Will add `order by created_at asc` to the query |
| `-created_at` | Will add `order by created_at desc` to the query |
| `updated_at` | Will add `order by updated_at asc` to the query |
| `-updated_at` | Will add `order by updated_at desc` to the query |

### List all the contacts for a given tag

This method lists all the contacts for a given tag.

**GET** `/tags/{:id}/contacts`

#### Parameters

| Name | Type | Description |
| --- | --- | --- |
| limit | integer | Indicates the page size. |
| page | integer | Indicates the page to return. |

#### Response

```json
{
  "data": [
    {
      "id": 117,
      "object": "contact",
      "hash_id": "h:Nvp2EaJrg9Pbl1YyX5",
      "first_name": "Pamela",
      "last_name": null,
      "nickname": null,
      "gender": "Rather not say",
      "gender_type": "O",
      "is_starred": false,
      "is_partial": false,
      "is_active": true,
      "is_dead": false,
      "is_me": false,
      "last_called": null,
      "last_activity_together": null,
      "stay_in_touch_frequency": null,
      "stay_in_touch_trigger_date": null,
      "information": {
        "relationships": {
          "love": {
            "total": 0,
            "contacts": []
          },
          "family": {
            "total": 0,
            "contacts": []
          },
          "friend": {
            "total": 0,
            "contacts": []
          },
          "work": {
            "total": 0,
            "contacts": []
          }
        },
        "dates": {
          "birthdate": {
            "is_age_based": null,
            "is_year_unknown": null,
            "date": null
          },
          "deceased_date": {
            "is_age_based": null,
            "is_year_unknown": null,
            "date": null
          }
        },
        "career": {
          "job": null,
          "company": null
        },
        "avatar": {
          "url": "https:\/\/monica.test\/storage\/avatars\/3e0c4041-5140-48fd-a58d-b45d9ea00c46.jpg?1579446390",
          "source": "default",
          "default_avatar_color": "#93521e"
        },
        "food_preferences": null,
        "how_you_met": {
          "general_information": null,
          "first_met_date": {
            "is_age_based": null,
            "is_year_unknown": null,
            "date": null
          },
          "first_met_through_contact": null
        }
      },
      "addresses": [],
      "tags": [
        {
          "id": 104,
          "object": "tag",
          "name": "dicta",
          "name_slug": "dicta",
          "account": {
            "id": 1
          },
          "created_at": "2020-01-19T15:06:30Z",
          "updated_at": "2020-01-19T15:06:30Z"
        }
      ],
      "statistics": {
        "number_of_calls": 0,
        "number_of_notes": 1,
        "number_of_activities": 0,
        "number_of_reminders": 0,
        "number_of_tasks": 0,
        "number_of_gifts": 5,
        "number_of_debts": 4
      },
      "contactFields": [],
      "notes": [
        {
          "id": 71,
          "object": "note",
          "body": "Mock Turtle yawned and shut his eyes.--'Tell her about the crumbs,' said the.",
          "is_favorited": true,
          "favorited_at": "2005-10-31T00:00:00Z",
          "url": "https:\/\/monica.test\/api\/notes\/71",
          "account": {
            "id": 1
          },
          "contact": {
            "id": 117,
            "object": "contact",
            "hash_id": "h:Nvp2EaJrg9Pbl1YyX5",
            "first_name": "Pamela",
            "last_name": null,
            "nickname": null,
            "complete_name": "Pamela",
            "initials": "P",
            "gender": "Rather not say",
            "gender_type": "O",
            "is_partial": false,
            "is_dead": false,
            "is_me": false,
            "information": {
              "birthdate": {
                "is_age_based": null,
                "is_year_unknown": null,
                "date": null
              },
              "deceased_date": {
                "is_age_based": null,
                "is_year_unknown": null,
                "date": null
              },
              "avatar": {
                "url": "https:\/\/monica.test\/storage\/avatars\/3e0c4041-5140-48fd-a58d-b45d9ea00c46.jpg?1579446390",
                "source": "default",
                "default_avatar_color": "#93521e"
              }
            },
            "url": "https:\/\/monica.test\/api\/contacts\/117",
            "account": {
              "id": 1
            }
          },
          "created_at": "2020-01-19T15:06:30Z",
          "updated_at": "2020-01-19T15:06:30Z"
        }
      ],
      "url": "https:\/\/monica.test\/api\/contacts\/117",
      "account": {
        "id": 1
      },
      "created_at": "2020-01-19T15:06:30Z",
      "updated_at": "2020-01-19T15:06:30Z"
    }
  ],
  "links": {
    "first": "https:\/\/monica.test\/api\/tags\/1\/contacts?page=1",
    "last": "https:\/\/monica.test\/api\/tags\/1\/contacts?page=5",
    "prev": null,
    "next": "https:\/\/monica.test\/api\/tags\/1\/contacts?page=2"
  },
  "meta": {
    "current_page": 1,
    "from": 1,
    "last_page": 5,
    "path": "https:\/\/monica.test\/api\/tags\/1\/contacts",
    "per_page": "1",
    "to": 1,
    "total": 5
  }
}
```

### Get a specific contact

**GET** `/contacts/:id`

#### Get a `real` contact

```json
{
  "data": {
    "id": 1,
    "object": "contact",
    "first_name": "Justen",
    "last_name": "Flatley",
    "nickname": "Rambo",
    "gender": "male",
    "is_partial": false,
    "is_dead": false,
    "last_called": null,
    "last_activity_together": {
      "date": "1977-07-17 00:00:00.000000",
      "timezone_type": 3,
      "timezone": "US\/Eastern"
    },
    "stay_in_touch_frequency": 5,
    "stay_in_touch_trigger_date": "2018-04-26T09:25:43Z",
    "information": {
      "relationships": {
        "love": {
          "total": 0,
          "contacts": []
        },
        "family": {
          "total": 0,
          "contacts": []
        },
        "friend": {
          "total": 0,
          "contacts": []
        },
        "work": {
          "total": 0,
          "contacts": []
        }
      },
      "dates": {
        "birthdate": {
          "is_age_based": null,
          "is_year_unknown": null,
          "date": null
        },
        "deceased_date": {
          "is_age_based": null,
          "is_year_unknown": null,
          "date": null
        }
      },
      "career": {
        "job": null,
        "company": null
      },
      "avatar": {
        "url": "https:\/\/randomuser.me\/api\/portraits\/men\/39.jpg",
        "source": "external"
      },
      "food_preferencies": "Alice was a paper label, with the distant sobs of the March Hare. Visit either you like: they're both mad.' 'But I don't believe you do lessons?' said Alice, 'because I'm not myself, you see.' 'I.",
      "how_you_met": {
        "general_information": "King exclaimed.",
        "first_met_date": {
          "is_age_based": null,
          "is_year_unknown": null,
          "date": null
        },
        "first_met_through_contact": {
          "id": 4,
          "object": "contact",
          "first_name": "Johnathon",
          "last_name": "Stark",
          "nickname": "Rambo",
          "gender": "male",
          "is_partial": true,
          "is_dead": false,
          "information": {
            "birthdate": {
              "is_age_based": false,
              "is_year_unknown": true,
              "date": "2017-09-24T00:00:00Z"
            },
            "deceased_date": {
              "is_age_based": null,
              "is_year_unknown": null,
              "date": null
            }
          },
          "account": {
            "id": 1
          }
        }
      }
    },
    "addresses": [],
    "tags": [],
    "statistics": {
      "number_of_calls": 0,
      "number_of_notes": 5,
      "number_of_activities": 3,
      "number_of_reminders": 0,
      "number_of_tasks": 3,
      "number_of_gifts": 7,
      "number_of_debts": 1
    },
    "account": {
      "id": 1
    },
    "created_at": "2017-12-12T09:57:15Z",
    "updated_at": "2017-12-12T09:57:15Z"
  }
}
```

#### Get a `partial` contact

Partial contacts are relationship contacts.

```json
{
  "data": {
    "id": 10,
    "object": "contact",
    "first_name": "Casandra",
    "last_name": null,
    "nickname": "Rambo",
    "gender": "female",
    "is_partial": true,
    "is_dead": false,
    "information": {
      "dates": {
        "birthdate": {
          "is_age_based": false,
          "is_year_unknown": false,
          "date": "1994-01-27T00:00:00Z"
        },
        "deceased_date": {
          "is_age_based": null,
          "is_year_unknown": null,
          "date": null
        }
      }
    },
    "account": {
      "id": 1
    },
    "created_at": "2017-12-12T09:57:16Z",
    "updated_at": "2017-12-12T09:57:16Z"
  }
}
```

#### Get a contact with contact fields information

Sometimes you need to have more information about a specific contact. This is especially useful in the context of the mobile application, where you need to reduce the amount of calls as much as possible.

The contact fields are added at the bottom of the JSON file that is returned. When doing this call, we also return the latest 3 notes that the user has written about the current contact.

**GET** `/contacts/:id?with=contactfields`

### Get the audit logs for the contact

Audit logs can be filtered by contact.

**GET** `/contacts/:id/logs`

#### Parameters

| Name | Type | Description |
| --- | --- | --- |
| limit | integer | Indicates the page size. |
| page | integer | Indicates the page to return. |

```json
{
  "data": [
    {
      "id": 1,
      "object": "auditlog",
      "author": {
        "id": 1,
        "name": null
      },
      "action": "contact_created",
      "objects": {
        "contact_name": "Celine Skiles",
        "contact_id": 1
      },
      "audited_at": "2020-02-05T22:02:44Z",
      "created_at": "2020-02-05T22:02:44Z",
      "updated_at": "2020-02-05T22:02:44Z"
    }
  ],
  "links": {
    "first": "https:\/\/monica.test\/api\/contacts\/1\/logs?page=1",
    "last": "https:\/\/monica.test\/api\/contacts\/1\/logs?page=1",
    "prev": null,
    "next": null
  },
  "meta": {
    "current_page": 1,
    "from": 1,
    "last_page": 1,
    "path": "https:\/\/monica.test\/api\/contacts\/1\/logs",
    "per_page": 15,
    "to": 1,
    "total": 1
  }
}
```

### Create a contact

**POST** `/contacts/`

#### Input

If a field is not required, you can send the `null` value as the content of the field.

| Name | Type | Description |
| --- | --- | --- |
| first_name | string | **Required**. The first name of the contact. Max 50 characters. |
| last_name | string | Last name of the contact. Max 100 characters. |
| nickname | string | Nickname of the contact. Max 100 characters. |
| gender_id | integer | **Required**. The Gender ID of the contact. Gender IDs are retrieved through the Gender's API. |
| birthdate_day | integer | Birthdate day of the contact. Required when is_birthdate_known is true and birthdate_is_age_based is false. |
| birthdate_month | integer | Birthdate month of the contact. Required when is_birthdate_known is true and birthdate_is_age_based is false. |
| birthdate_year | integer | Birthdate year of the contact. |
| birthdate_is_age_based | boolean | Indicates whether the birthdate is age based or not. |
| is_birthdate_known | boolean | **Required**. |
| birthdate_age | integer | The number of years between the birthdate and the current year. Required when is_birthdate_known is true and birthdate_is_age_based is true. |
| is_partial | boolean | Indicates whether a contact is `real` (false) or `partial` (true). |
| is_deceased | boolean | **Required**. Indicates whether a contact is deceased. |
| is_deceased_date_known | boolean | **Required**. |
| deceased_date_add_reminder | boolean | Whether add a reminder for the deceased date or not. |
| deceased_date_day | integer | Deceased day of the contact. |
| deceased_date_month | integer | Deceased month of the contact. |
| deceased_date_year | integer | Deceased year of the contact. |
| deceased_date_is_age_based | boolean | Indicates whether the deceased_date is age based or not. |

#### Example

```json
{
  "first_name": "henri",
  "last_name": "troyat",
  "nickname": "Rambo",
  "gender_id": 1,
  "birthdate_day": null,
  "birthdate_month": null,
  "birthdate_year": null,
  "is_birthdate_known": false,
  "birthdate_is_age_based": true,
  "is_birthdate_known": false,
  "birthdate_age": 29,
  "is_partial": false,
  "is_deceased": true,
  "deceased_date_day": 2,
  "deceased_date_month": 2,
  "deceased_date_year": 2017,
  "deceased_date_is_age_based": false,
  "is_deceased_date_known": true,
}
```

#### Response

The API call returns a contact object if the call succeeds.

```json
{
  "data": {
    "id": 206,
    "object": "contact",
    "hash_id": "h:j9ePOdJb0XdbB6EN1R",
    "first_name": "henri",
    "last_name": "troyat",
    "nickname": "Rambo",
    "complete_name": "henri troyat (Rambo) ⚰",
    "description": null,
    "gender": "Man",
    "gender_type": "M",
    "is_starred": false,
    "is_partial": false,
    "is_active": true,
    "is_dead": true,
    "is_me": false,
    "last_called": null,
    "last_activity_together": null,
    "stay_in_touch_frequency": null,
    "stay_in_touch_trigger_date": null,
    "information": {
      "relationships": {
        "love": {
          "total": 0,
          "contacts": []
        },
        "family": {
          "total": 0,
          "contacts": []
        },
        "friend": {
          "total": 0,
          "contacts": []
        },
        "work": {
          "total": 0,
          "contacts": []
        }
      },
      "dates": {
        "birthdate": {
          "is_age_based": null,
          "is_year_unknown": null,
          "date": null
        },
        "deceased_date": {
          "is_age_based": false,
          "is_year_unknown": false,
          "date": "2017-02-02T00:00:00Z"
        }
      },
      "career": {
        "job": null,
        "company": null
      },
      "avatar": {
        "url": "https:\/\/monica.test\/storage\/avatars\/600a4566-89fb-4768-a825-0aa19355b722.jpg?1580520601",
        "source": "default",
        "default_avatar_color": "#b3d5fe"
      },
      "food_preferences": null,
      "how_you_met": {
        "general_information": null,
        "first_met_date": {
          "is_age_based": null,
          "is_year_unknown": null,
          "date": null
        },
        "first_met_through_contact": null
      }
    },
    "addresses": [],
    "tags": [],
    "statistics": {
      "number_of_calls": 0,
      "number_of_notes": 0,
      "number_of_activities": 0,
      "number_of_reminders": 0,
      "number_of_tasks": 0,
      "number_of_gifts": 0,
      "number_of_debts": 0
    },
    "url": "https:\/\/monica.test\/api\/contacts\/206",
    "account": {
      "id": 1
    },
    "created_at": "2020-02-01T01:30:01Z",
    "updated_at": "2020-02-01T01:30:01Z"
  }
}
```

### Update a contact

**PUT** `/contacts/:id`

#### Input

| Name | Type | Description |
| --- | --- | --- |
| first_name | string | **Required**. The first name of the contact. Max 50 characters. |
| last_name | string | Last name of the contact. Max 100 characters. |
| nickname | string | Nickname of the contact. Max 100 characters. |
| gender_id | integer | **Required**. The Gender ID of the contact. Gender IDs are retrieved through the Gender's API. |
| birthdate_day | integer | Birthdate day of the contact. Required when is_birthdate_known is true and birthdate_is_age_based is false. |
| birthdate_month | integer | Birthdate month of the contact. Required when is_birthdate_known is true and birthdate_is_age_based is false. |
| birthdate_year | integer | Birthdate year of the contact. |
| birthdate_is_age_based | boolean | Indicates whether the birthdate is age based or not. |
| is_birthdate_known | boolean | **Required**. |
| birthdate_age | integer | The number of years between the birthdate and the current year. Required when is_birthdate_known is true and birthdate_is_age_based is true. |
| is_partial | boolean | Indicates whether a contact is `real` (false) or `partial` (true). |
| is_deceased | boolean | **Required**. Indicates whether a contact is deceased. |
| is_deceased_date_known | boolean | **Required**. |
| deceased_date_add_reminder | boolean | Whether add a reminder for the deceased date or not. |
| deceased_date_day | integer | Deceased day of the contact. |
| deceased_date_month | integer | Deceased month of the contact. |
| deceased_date_year | integer | Deceased year of the contact. |
| deceased_date_is_age_based | boolean | Indicates whether the deceased_date is age based or not. |

#### Example

```json
{
    "first_name": "henri",
    "last_name": "troyat",
    "nickname": "Rambo",
    "gender_id": 1,
    "birthdate_day": null,
    "birthdate_month": null,
    "birthdate_year": null,
    "birthdate_is_age_based": true,
    "is_birthdate_known": false,
    "birthdate_age": 29,
    "is_partial": false,
    "is_deceased": true,
    "deceased_date": null,
    "deceased_date_is_age_based": true,
    "deceased_date_is_year_unknown": false,
    "deceased_date_age": 98,
    "is_deceased_date_known": false
}
```

#### Response

```json
{
  "data": {
    "id": 1,
    "object": "contact",
    "hash_id": "h:Y5LOkAdWNDqgVomKPv",
    "first_name": "henri",
    "last_name": "troyat",
    "nickname": "Rambo",
    "complete_name": "henri troyat (Rambo) ⚰",
    "description": "kjlkjkl",
    "gender": "Man",
    "gender_type": "M",
    "is_starred": false,
    "is_partial": false,
    "is_active": true,
    "is_dead": true,
    "is_me": false,
    "last_called": null,
    "last_activity_together": "2019-05-19T00:00:00.000000Z",
    "stay_in_touch_frequency": null,
    "stay_in_touch_trigger_date": null,
    "information": {
      "relationships": {
        "love": {
          "total": 0,
          "contacts": []
        },
        "family": {
          "total": 0,
          "contacts": []
        },
        "friend": {
          "total": 0,
          "contacts": []
        },
        "work": {
          "total": 0,
          "contacts": []
        }
      },
      "dates": {
        "birthdate": {
          "is_age_based": null,
          "is_year_unknown": null,
          "date": null
        },
        "deceased_date": {
          "is_age_based": null,
          "is_year_unknown": null,
          "date": null
        }
      },
      "career": {
        "job": null,
        "company": null
      },
      "avatar": {
        "url": "https:\/\/monica.test\/storage\/avatars\/f7cd73b9-5027-4f66-ab8d-1d578b7a2274.jpg?1580520815",
        "source": "default",
        "default_avatar_color": "#ff9807"
      },
      "food_preferences": "First, she tried the roots of trees, and I've tried to get dry very soon. 'Ahem!' said the Cat. 'I don't think--' 'Then you shouldn't talk,' said the Mock Turtle, capering wildly about. 'Change.",
      "how_you_met": {
        "general_information": null,
        "first_met_date": {
          "is_age_based": null,
          "is_year_unknown": null,
          "date": null
        },
        "first_met_through_contact": null
      }
    },
    "addresses": [],
    "tags": [],
    "statistics": {
      "number_of_calls": 0,
      "number_of_notes": 2,
      "number_of_activities": 2,
      "number_of_reminders": 0,
      "number_of_tasks": 0,
      "number_of_gifts": 7,
      "number_of_debts": 0
    },
    "url": "https:\/\/monica.test\/api\/contacts\/1",
    "account": {
      "id": 1
    },
    "created_at": "2020-01-19T15:06:17Z",
    "updated_at": "2020-02-01T01:33:35Z"
  }
}
```

### Update a contact career

**PUT** `/contacts/:id/work`

#### Input

| Name | Type | Description |
| --- | --- | --- |
| job | string | The job title. Max 255 characters. |
| company | string | The company name. Max 255 characters. |

#### Example

```json
{
  "job": "Big boss",
  "company": "Monicahq"
}
```

#### Response

```json
{
  "data": {
    "id": 1,
    "object": "contact",
    "hash_id": "h:Y5LOkAdWNDqgVomKPv",
    "first_name": "henri",
    "last_name": "troyat",
    "nickname": "Rambo",
    "complete_name": "henri troyat (Rambo) ⚰",
    "description": "kjlkjkl",
    "gender": "Man",
    "gender_type": "M",
    "is_starred": false,
    "is_partial": false,
    "is_active": true,
    "is_dead": true,
    "is_me": false,
    "last_called": null,
    "last_activity_together": "2019-05-19T00:00:00.000000Z",
    "stay_in_touch_frequency": null,
    "stay_in_touch_trigger_date": null,
    "information": {
      "relationships": {
        "love": {
          "total": 0,
          "contacts": []
        },
        "family": {
          "total": 0,
          "contacts": []
        },
        "friend": {
          "total": 0,
          "contacts": []
        },
        "work": {
          "total": 0,
          "contacts": []
        }
      },
      "dates": {
        "birthdate": {
          "is_age_based": null,
          "is_year_unknown": null,
          "date": null
        },
        "deceased_date": {
          "is_age_based": null,
          "is_year_unknown": null,
          "date": null
        }
      },
      "career": {
        "job": "sales",
        "company": "dunder mifflin"
      },
      "avatar": {
        "url": "https:\/\/monica.test\/storage\/avatars\/f7cd73b9-5027-4f66-ab8d-1d578b7a2274.jpg?1580520930",
        "source": "default",
        "default_avatar_color": "#ff9807"
      },
      "food_preferences": "First, she tried the roots of trees, and I've tried to get dry very soon. 'Ahem!' said the Cat. 'I don't think--' 'Then you shouldn't talk,' said the Mock Turtle, capering wildly about. 'Change.",
      "how_you_met": {
        "general_information": null,
        "first_met_date": {
          "is_age_based": null,
          "is_year_unknown": null,
          "date": null
        },
        "first_met_through_contact": null
      }
    },
    "addresses": [],
    "tags": [],
    "statistics": {
      "number_of_calls": 0,
      "number_of_notes": 2,
      "number_of_activities": 2,
      "number_of_reminders": 0,
      "number_of_tasks": 0,
      "number_of_gifts": 7,
      "number_of_debts": 0
    },
    "url": "https:\/\/monica.test\/api\/contacts\/1",
    "account": {
      "id": 1
    },
    "created_at": "2020-01-19T15:06:17Z",
    "updated_at": "2020-02-01T01:37:50Z"
  }
}
```

### Delete a contact

**DELETE** `/contacts/:id`

#### Response

The response sends back the id that was just deleted.

```json
{
  "deleted": true,
  "id": 93135
}
```

### Search

You can search specific contacts. Here are the fields that search takes into account:

- first name
- last name
- food preferencies
- job
- company.

**GET** `/contacts?query=regis`

#### Input

| Name | Type | Description |
| --- | --- | --- |
| query | string | **Required**. The string you'd like to search. |

#### Response

This call returns a collection of contacts. Note that `body.meta.query` contains the query you wanted to search.

```json
{
    "data": [
        {
            "id": 117,
            "object": "contact",
            "first_name": "Collin",
            "last_name": "Moen",
            "nickname": "Rambo",
            "gender": "Man",
            "is_partial": false,
            "is_dead": false,
            "last_called": null,
            "last_activity_together": null,
            "stay_in_touch_frequency": 5,
            "stay_in_touch_trigger_date": "2018-04-26T09:25:43Z",
            "information": {
                "relationships": {
                  "love": {
                    "total": 0,
                    "contacts": []
                  },
                  "family": {
                    "total": 0,
                    "contacts": []
                  },
                  "friend": {
                    "total": 0,
                    "contacts": []
                  },
                  "work": {
                    "total": 0,
                    "contacts": []
                  }
                },
                "dates": {
                    "birthdate": {
                        "is_age_based": null,
                        "is_year_unknown": null,
                        "date": null
                    },
                    "deceased_date": {
                        "is_age_based": null,
                        "is_year_unknown": null,
                        "date": null
                    }
                },
                "career": {
                    "job": null,
                    "company": null
                },
                "avatar": {
                    "url": null,
                    "source": null,
                    "default_avatar_color": "#fdb660"
                },
                "food_preferencies": null,
                "how_you_met": {
                    "general_information": null,
                    "first_met_date": {
                        "is_age_based": null,
                        "is_year_unknown": null,
                        "date": null
                    },
                    "first_met_through_contact": null
                }
            },
            "addresses": [
                {
                    "id": 7,
                    "object": "address",
                    "name": "beatae",
                    "street": "88761 Hallie Walk Apt. 685",
                    "city": null,
                    "province": null,
                    "postal_code": null,
                    "country": {
                        "id": 154,
                        "object": "country",
                        "name": "Montenegro",
                        "iso": "me"
                    },
                    "created_at": "2018-02-18T10:36:02Z",
                    "updated_at": "2018-02-18T10:36:02Z"
                }
            ],
            "tags": [],
            "statistics": {
                "number_of_calls": 0,
                "number_of_notes": 2,
                "number_of_activities": 0,
                "number_of_reminders": 1,
                "number_of_tasks": 0,
                "number_of_gifts": 0,
                "number_of_debts": 4
            },
            "account": {
                "id": 1
            },
            "created_at": "2018-02-18T10:36:02Z",
            "updated_at": "2018-02-25T11:17:18Z"
        }
    ],
    "links": {
        "first": "http://monica.test/api/contacts?page=1",
        "last": "http://monica.test/api/contacts?page=1",
        "prev": null,
        "next": null
    },
    "meta": {
        "current_page": 1,
        "from": 1,
        "last_page": 1,
        "path": "http://monica.test/api/contacts",
        "per_page": 15,
        "to": 1,
        "total": 1,
        "query": "collin"
    }
}
```

---

## Notes

### Overview

The Note object allows to associate notes to contacts. A note has to be associated with an existing contact - it can't be orphan.

A note can be favorited. When favorited, it will be display on the dashboard inside the application.

When retrieving a note, we always also return some basic information about the related contact.

### List all the notes in your account

**GET** `/notes/`

#### Parameters

| Name | Type | Description |
| --- | --- | --- |
| limit | integer | Indicates the page size. |
| page | integer | Indicates the page to return. |

#### Response

```json
{
  "data": [
    {
      "id": 4724,
      "object": "note",
      "body": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris. Maecenas congue ligula ac quam viverra nec consectetur ante hendrerit. Donec et mollis dolor. Praesent et diam eget libero egestas mattis sit amet vitae augue. Nam tincidunt congue enim, ut porta lorem lacinia consectetur. Donec ut libero sed arcu vehicula ultricies a non tortor.",
      "is_favorited": true,
      "favorited_at": "2017-12-04T00:00:00Z",
      "account": {
        "id": 1
      },
      "contact": {
        "id": 1,
        "object": "contact",
        "first_name": "Usher",
        "last_name": "Misste",
        "gender": "male",
        "is_partial": false,
        "information": {
          "dates": [
            {
              "name": "birthdate",
              "is_birthdate_approximate": "exact",
              "birthdate": "1983-10-23T19:10:42Z"
            }
          ]
        },
        "account": {
          "id": 1
        }
      },
      "created_at": "2017-10-07T09:00:35Z",
      "updated_at": "2017-10-07T09:00:35Z"
    }
  ],
  "links": {
    "first": "https://app.monicahq.com/api/contacts/1/notes?page=1",
    "last": "https://app.monicahq.com/api/contacts/1/notes?page=1",
    "prev": null,
    "next": null
  },
  "meta": {
    "current_page": 1,
    "from": 1,
    "last_page": 1,
    "path": "https://app.monicahq.com/api/contacts/1/notes",
    "per_page": 10,
    "to": 2,
    "total": 2
  }
}
```

### List all the notes of a specific contact

**GET** `/contacts/:id/notes`

#### Response

```json
{
  "data": [
    {
      "id": 4724,
      "object": "note",
      "body": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris. Maecenas congue ligula ac quam viverra nec consectetur ante hendrerit. Donec et mollis dolor. Praesent et diam eget libero egestas mattis sit amet vitae augue. Nam tincidunt congue enim, ut porta lorem lacinia consectetur. Donec ut libero sed arcu vehicula ultricies a non tortor.",
      "is_favorited": true,
      "favorited_at": "2017-12-04T00:00:00Z",
      "account": {
        "id": 1
      },
      "contact": {
        "id": 1,
        "object": "contact",
        "first_name": "Usher",
        "last_name": "Misste",
        "gender": "male",
        "is_partial": false,
        "information": {
          "dates": [
            {
              "name": "birthdate",
              "is_birthdate_approximate": "exact",
              "birthdate": "1983-10-23T19:10:42Z"
            }
          ]
        },
        "account": {
          "id": 1
        }
      },
      "created_at": "2017-10-07T09:00:35Z",
      "updated_at": "2017-10-07T09:00:35Z"
    }
  ],
  "links": {
    "first": "https://app.monicahq.com/api/contacts/1/notes?page=1",
    "last": "https://app.monicahq.com/api/contacts/1/notes?page=1",
    "prev": null,
    "next": null
  },
  "meta": {
    "current_page": 1,
    "from": 1,
    "last_page": 1,
    "path": "https://app.monicahq.com/api/contacts/1/notes",
    "per_page": 10,
    "to": 2,
    "total": 2
  }
}
```

### Get a specific note

**GET** `/notes/:id`

#### Response

```json
{
  "data": {
    "id": 4724,
    "object": "note",
    "body": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris. Maecenas congue ligula ac quam viverra nec consectetur ante hendrerit. Donec et mollis dolor. Praesent et diam eget libero egestas mattis sit amet vitae augue. Nam tincidunt congue enim, ut porta lorem lacinia consectetur. Donec ut libero sed arcu vehicula ultricies a non tortor.",
    "is_favorited": true,
      "favorited_at": "2017-12-04T00:00:00Z",
    "account": {
      "id": 1
    },
    "contact": {
      "id": 1,
      "object": "contact",
      "first_name": "Henri",
      "last_name": "Troyat",
      "gender": "female",
      "is_partial": false,
      "information": {
        "dates": [
          {
            "name": "birthdate",
            "is_birthdate_approximate": "exact",
            "birthdate": "1983-10-23T19:10:42Z"
          }
        ]
      },
      "account": {
        "id": 1
      }
    },
    "created_at": "2017-10-07T09:00:35Z",
    "updated_at": "2017-10-07T09:00:35Z"
  }
}
```

### Create a note

**POST** `/notes/`

#### Input

| Name | Type | Description |
| --- | --- | --- |
| body | string | **Required**. The body of the note. Max 100000 characters. |
| contact_id | integer | **Required**. The ID of the contact that the note is associated with. |
| is_favorited | integer | **Required**. Indicates whether the note is favorited or not. Can be `0` (false) or `1` (true). |

#### Example

```json
{
  "body": "This is a sample of a note.",
  "contact_id": 1,
  "is_favorited": 0
}
```

#### Response

The API call returns a note object if the call succeeds.

```json
{
  "data": {
    "id": 4724,
    "object": "note",
    "body": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris. Maecenas congue ligula ac quam viverra nec consectetur ante hendrerit. Donec et mollis dolor. Praesent et diam eget libero egestas mattis sit amet vitae augue. Nam tincidunt congue enim, ut porta lorem lacinia consectetur. Donec ut libero sed arcu vehicula ultricies a non tortor.",
    "is_favorited": true,
    "favorited_at": null,
    "account": {
      "id": 1
    },
    "contact": {
      "id": 1,
      "object": "contact",
      "first_name": "Henri",
      "last_name": "Troyat",
      "gender": "female",
      "is_partial": false,
      "information": {
        "dates": [
          {
            "name": "birthdate",
            "is_birthdate_approximate": "exact",
            "birthdate": "1983-10-23T19:10:42Z"
          }
        ]
      },
      "account": {
        "id": 1
      }
    },
    "created_at": "2017-10-07T09:00:35Z",
    "updated_at": "2017-10-07T09:00:35Z"
  }
}
```

### Update a note

**PUT** `/notes/:id`

#### Input

| Name | Type | Description |
| --- | --- | --- |
| body | string | **Required**. The body of the note. Max 100000 characters. |
| contact_id | integer | **Required**. The ID of the contact that the note is associated with. |
| is_favorited | integer | **Required**. Indicates whether the note is favorited or not. Can be `0` (false) or `1` (true). |

#### Example

```json
{
  "body": "This is a test that is updated",
  "contact_id": 3
}
```

#### Response

```json
{
  "data": {
    "id": 4724,
    "object": "note",
    "body": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris. Maecenas congue ligula ac quam viverra nec consectetur ante hendrerit. Donec et mollis dolor. Praesent et diam eget libero egestas mattis sit amet vitae augue. Nam tincidunt congue enim, ut porta lorem lacinia consectetur. Donec ut libero sed arcu vehicula ultricies a non tortor.",
    "is_favorited": true,
    "favorited_at": "2017-12-04T00:00:00Z",
    "account": {
      "id": 1
    },
    "contact": {
      "id": 1,
      "object": "contact",
      "first_name": "Henri",
      "last_name": "Troyat",
      "gender": "female",
      "is_partial": false,
      "information": {
        "dates": [
          {
            "name": "birthdate",
            "is_birthdate_approximate": "exact",
            "birthdate": "1983-10-23T19:10:42Z"
          }
        ]
      },
      "account": {
        "id": 1
      }
    },
    "created_at": "2017-10-07T09:00:35Z",
    "updated_at": "2017-10-07T09:00:35Z"
  }
}
```

### Delete a note

**DELETE** `/notes/:id`

#### Response

The response sends back the id that was just deleted.

```json
{
  "deleted": true,
  "id": 31
}
```

---

## Activities

### Overview

The Activity object represents activities made with one or more contacts. Use it to keep track of what you've done. An activity can't be orphan - it needs to be linked to at least one contact.

When retrieving an activity, we always also return some basic information about the related contact(s).

### List all the activities in your account

**GET** `/activities/`

#### Parameters

| Name | Type | Description |
| --- | --- | --- |
| limit | integer | Indicates the page size. |
| page | integer | Indicates the page to return. |

#### Response

```json
{
  "data": [
    {
      "id": 1,
      "object": "activity",
      "summary": "",
      "description": "On a mangé avec papi et mamie au restaurant indien.",
      "happened_at": "2016-10-04",
      "activity_type": {
                "id": 12,
                "object": "activityType",
                "name": "návštěva zápasu",
                "location_type": null,
                "activity_type_category": {
                    "id": 4,
                    "object": "activityTypeCategory",
                    "name": "Cultural activities",
                    "account": {
                        "id": 1
                    },
                    "created_at": null,
                    "updated_at": null
                },
                "account": {
                    "id": 1
                },
                "created_at": null,
                "updated_at": null
            },
      "attendees": {
        "total": 1,
        "contacts": [
          {
            "id": 1,
            "object": "contact",
            "hash_id": "h:X5LOkAdWNDqgVomKPv",
            "first_name": "Henri",
            "last_name": "Troyat",
            "nickname": "",
            "complete_name": "Henri Troyat",
            "initials": "HT",
            "gender": "Female",
            "gender_type": "F",
            "is_partial": false,
            "is_dead": false,
            "is_me": false,
            "information": {
              "dates": [
                {
                  "name": "birthdate",
                  "is_birthdate_approximate": "exact",
                  "birthdate": "1983-10-23T19:10:42Z"
                }
              ]
            },
            "account": {
              "id": 1
            }
          }
        ]
      },
      "account": {
        "id": 1
      },
      "created_at": "2016-10-07T11:59:14Z",
      "updated_at": "2017-05-03T01:42:28Z"
    }
  ],
  "links": {
    "first": "https:\/\/app.monicahq.com\/api\/activities?page=1",
    "last": "https:\/\/app.monicahq.com\/api\/activities?page=1",
    "prev": null,
    "next": null
  },
  "meta": {
    "current_page": 1,
    "from": 1,
    "last_page": 1,
    "path": "https:\/\/app.monicahq.com\/api\/activities",
    "per_page": 10,
    "to": 5,
    "total": 5
  }
}
```

### List all the activities of a specific contact

**GET** `/contacts/:id/activities`

#### Response

```json
{
  "data": [
    {
      "id": 2,
      "object": "activity",
      "summary": "Lunch with Dwight",
      "description": "We play handball and it was just awesome. He told me about a new girl he likes Cathy Simms, so he has to be careful.",
      "happened_at": "2016-10-18",
      "activity_type": {
                "id": 12,
                "object": "activityType",
                "name": "návštěva zápasu",
                "location_type": null,
                "activity_type_category": {
                    "id": 4,
                    "object": "activityTypeCategory",
                    "name": "Cultural activities",
                    "account": {
                        "id": 1
                    },
                    "created_at": null,
                    "updated_at": null
                },
                "account": {
                    "id": 1
                },
                "created_at": null,
                "updated_at": null
            },
      "attendees": {
        "total": 1,
        "contacts": [
          {
            "id": 8,
            "object": "contact",
            "hash_id": "h:AlKmTUoPDqgVomKPv",
            "first_name": "Jim",
            "last_name": "Halpert",
            "nickname": "",
            "complete_name": "Jim Halpert",
            "initials": "JH",
            "gender": "Male",
            "gender_type": "M",
            "is_partial": false,
            "is_dead": false,
            "is_me": false,
            "information": {
              "dates": [
                {
                  "name": "birthdate",
                  "is_birthdate_approximate": "exact",
                  "birthdate": "1978-10-01T16:20:55Z"
                }
              ]
            },
            "account": {
              "id": 1
            }
          }
        ]
      },
      "account": {
        "id": 1
      },
      "created_at": "2016-10-18T23:58:18Z",
      "updated_at": "2017-06-07T13:09:47Z"
    }
  ],
  "links": {
    "first": "https:\/\/app.monicahq.com\/api\/contacts\/8\/activities?page=1",
    "last": "https:\/\/app.monicahq.com\/api\/contacts\/8\/activities?page=1",
    "prev": null,
    "next": null
  },
  "meta": {
    "current_page": 1,
    "from": 1,
    "last_page": 1,
    "path": "https:\/\/app.monicahq.com\/api\/contacts\/8\/activities",
    "per_page": 10,
    "to": 1,
    "total": 1
  }
}
```

### Get a specific activity

**GET** `/activities/:id`

#### Response

```json
{
  "data": {
    "id": 2,
    "object": "activity",
    "summary": "Lunch with Dwight",
    "description": "We play handball and it was just awesome. He told me about a new girl he likes Cathy Simms, so he has to be careful.",
    "happened_at": "2016-10-18",
    "activity_type": {
                "id": 12,
                "object": "activityType",
                "name": "návštěva zápasu",
                "location_type": null,
                "activity_type_category": {
                    "id": 4,
                    "object": "activityTypeCategory",
                    "name": "Cultural activities",
                    "account": {
                        "id": 1
                    },
                    "created_at": null,
                    "updated_at": null
                },
                "account": {
                    "id": 1
                },
                "created_at": null,
                "updated_at": null
            },
    "attendees": {
      "total": 1,
      "contacts": [
        {
          "id": 8,
          "object": "contact",
          "hash_id": "h:AlKmTUoPDqgVomKPv",
          "first_name": "Jim",
          "last_name": "Halpert",
          "nickname": "",
          "complete_name": "Jim Halpert",
          "initials": "JH",
          "gender": "Male",
          "gender_type": "M",
          "is_partial": false,
          "is_dead": false,
          "is_me": false,
          "information": {
            "dates": [
              {
                "name": "birthdate",
                "is_birthdate_approximate": "exact",
                "birthdate": "1978-10-01T16:20:55Z"
              }
            ]
          },
          "account": {
            "id": 1
          }
        }
      ]
    },
    "account": {
      "id": 1
    },
    "created_at": "2016-10-18T23:58:18Z",
    "updated_at": "2017-06-07T13:09:47Z"
  }
}
```

### Create an activity

**POST** `/activities/`

#### Input

| Name | Type | Description |
| --- | --- | --- |
| activity_type_id | integer | **Required**. The ID of the type of activity that the activity is associated with. |
| summary | string | **Required**. A short description of the activity. Max 255 characters. |
| description | string | An optional comment to add more details on what happened. Max 1000000 characters. |
| happened_at | string | **Required**. The date the event happened. Can be in the past or future - the latter being dumb, but well. Format: YYYY-MM-DD. |
| contacts | array | **Required**. The ID of contacts the activity is associated with. |
| emotions | array | The ID of emotions the activity is associated with. |

#### Example

```json
{
  "activity_type_id": 2,
  "summary": "We ate at an awesome restaurant.",
  "description": "We ate way too much, we had fun and we promised we'd see each other again in a couple of weeks.",
  "happened_at": "2018-02-02",
  "contacts": [1,3,5]
}
```

#### Response

The API call returns an Activity object if the call succeeds.

```json
{
  "data": {
    "id": 4670,
    "object": "activity",
    "summary": "We ate at an awesome restaurant.",
    "description": "We ate way too much, we had fun and we promised we'd see each other again in a couple of weeks.",
    "happened_at": "2018-02-02",
    "activity_type": {
                "id": 12,
                "object": "activityType",
                "name": "návštěva zápasu",
                "location_type": null,
                "activity_type_category": {
                    "id": 4,
                    "object": "activityTypeCategory",
                    "name": "Cultural activities",
                    "account": {
                        "id": 1
                    },
                    "created_at": null,
                    "updated_at": null
                },
                "account": {
                    "id": 1
                },
                "created_at": null,
                "updated_at": null
            },
    "attendees": {
      "total": 3,
      "contacts": [
        {
          "id": 1,
          "object": "contact",
          "hash_id": "h:X5LOkAdWNDqgVomKPv",
          "first_name": "Henri",
          "last_name": "Troyat",
          "nickname": "",
          "complete_name": "Henri Troyat",
          "initials": "HT",
          "gender": "Female",
          "gender_type": "F",
          "is_partial": false,
          "is_dead": false,
          "is_me": false,
          "information": {
            "dates": [
              {
                "name": "birthdate",
                "is_birthdate_approximate": "exact",
                "birthdate": "1983-10-23T19:10:42Z"
              }
            ]
          },
          "account": {
            "id": 1
          }
        }
      ]
    },
    "account": {
      "id": 1
    },
    "created_at": "2017-10-25T12:46:55Z",
    "updated_at": "2017-10-25T12:46:55Z"
  }
}
```

### Update an activity

**PUT** `/activities/:id`

#### Input

| Name | Type | Description |
| --- | --- | --- |
| activity_type_id | integer | **Required**. The ID of the type of activity that the activity is associated with. |
| summary | string | **Required**. A short description of the activity. Max 255 characters. |
| description | string | An optional comment to add more details on what happened. Max 1000000 characters. |
| happened_at | string | **Required**. The date the event happened. Can be in the past or future - the latter being dumb, but well. Format: YYYY-MM-DD. |
| contacts | array | **Required**. The ID of contacts the activity is associated with. |
| emotions | array | The ID of emotions the activity is associated with. |

#### Example

```json
{
  "activity_type_id": 2,
  "summary": "We ate at an awesome restaurant.",
  "description": "We ate way too much, we had fun and we promised we'd see each other again in a couple of weeks.",
  "happened_at": "2018-02-02",
  "contacts": [1,3]
}
```

#### Response

```json
{
  "data": {
    "id": 4670,
    "object": "activity",
    "summary": "We ate at an awesome restaurant.",
    "description": "We ate way too much, we had fun and we promised we'd see each other again in a couple of weeks.",
    "happened_at": "2018-02-02",
    "activity_type": {
                "id": 12,
                "object": "activityType",
                "name": "návštěva zápasu",
                "location_type": null,
                "activity_type_category": {
                    "id": 4,
                    "object": "activityTypeCategory",
                    "name": "Cultural activities",
                    "account": {
                        "id": 1
                    },
                    "created_at": null,
                    "updated_at": null
                },
                "account": {
                    "id": 1
                },
                "created_at": null,
                "updated_at": null
            },
    "attendees": {
      "total": 2,
      "contacts": [
        {
          "id": 1,
          "object": "contact",
          "hash_id": "h:X5LOkAdWNDqgVomKPv",
          "first_name": "Henri",
          "last_name": "Troyat",
          "nickname": "",
          "complete_name": "Henri Troyat",
          "initials": "HT",
          "gender": "Female",
          "gender_type": "F",
          "is_partial": false,
          "is_dead": false,
          "is_me": false,
          "information": {
            "dates": [
              {
                "name": "birthdate",
                "is_birthdate_approximate": "exact",
                "birthdate": "1983-10-23T19:10:42Z"
              }
            ]
          },
          "account": {
            "id": 1
          }
        }
      ]
    },
    "account": {
      "id": 1
    },
    "created_at": "2017-10-25T12:46:55Z",
    "updated_at": "2017-10-25T12:46:55Z"
  }
}
```

### Delete an activity

**DELETE** `/activities/:id`

#### Response

The response sends back the id that was just deleted.

```json
{
  "deleted": true,
  "id": 31
}
```

---

## Reminders

### Overview

The Reminder object allows to add reminders about your contacts.

A reminder is a complex object in Monica. There are two types of reminders:

- unique reminder (`frequency_type` == `one_time`),
- recurring reminder (`frequency_type` == `week` | `month` | `year`).

When a reminder is recurrent, the `frequency_number` indicates the number of days|months|years between each occurence.

It's important to note that when a birthdate is entered for a contact, the system will automatically create a reminder for this birthday. In your code, make sure that you don't explicitely create a reminder for birthdays.

When a reminder is supposed to be triggered, if the instance is set to send emails or if the account is on the paid plan, an email will be sent automatically to the user with the reminder as its content.

When retrieving a reminder, we always also return some basic information about the related contact.

### List all the reminders in your account

**GET** `/reminders/`

#### Parameters

| Name | Type | Description |
| --- | --- | --- |
| limit | integer | Indicates the page size. |
| page | integer | Indicates the page to return. |

#### Response

```json
{
  "data": [
    {
      "id": 2,
      "object": "reminder",
      "title": "Wish happy birthday to Danny",
      "description": null,
      "frequency_type": "year",
      "frequency_number": 1,
      "last_triggered_date": null,
      "next_expected_date": "2017-10-23T00:00:18Z",
      "account": {
        "id": 1
      },
      "contact": {
        "id": 1,
        "object": "contact",
        "first_name": "Danny",
        "last_name": "Troyat",
        "gender": "female",
        "is_partial": false,
        "information": {
          "dates": [
            {
              "name": "birthdate",
              "is_birthdate_approximate": "exact",
              "birthdate": "1983-10-23T19:10:42Z"
            }
          ]
        },
        "account": {
          "id": 1
        }
      },
      "created_at": "2016-10-07T11:53:43Z",
      "updated_at": "2017-06-16T19:04:54Z"
    }
  ],
  "links": {
    "first": "https://app.monicahq.com/api/reminders?page=1",
    "last": "https://app.monicahq.com/api/reminders?page=3",
    "prev": null,
    "next": "https://app.monicahq.com/api/reminders?page=2"
  },
  "meta": {
    "current_page": 1,
    "from": 1,
    "last_page": 3,
    "path": "https://app.monicahq.com/api/reminders",
    "per_page": 10,
    "to": 10,
    "total": 22
  }
}
```

### List all the reminders of a specific contact

**GET** `/contacts/:id/reminders`

#### Response

```json
{
  "data": [
    {
      "id": 2,
      "object": "reminder",
      "title": "Wish happy birthday to Jean",
      "description": null,
      "frequency_type": "year",
      "frequency_number": 1,
      "last_triggered_date": null,
      "next_expected_date": "2017-10-23T00:00:18Z",
      "account": {
        "id": 1
      },
      "contact": {
        "id": 1,
        "object": "contact",
        "first_name": "Jean",
        "last_name": "Valjean",
        "gender": "female",
        "is_partial": false,
        "information": {
          "dates": [
            {
              "name": "birthdate",
              "is_birthdate_approximate": "exact",
              "birthdate": "1983-10-23T19:10:42Z"
            }
          ]
        },
        "account": {
          "id": 1
        }
      },
      "created_at": "2016-10-07T11:53:43Z",
      "updated_at": "2017-06-16T19:04:54Z"
    }
  ],
  "links": {
    "first": "https:\/\/app.monicahq.com\/api\/contacts\/1\/reminders?page=1",
    "last": "https:\/\/app.monicahq.com\/api\/contacts\/1\/reminders?page=1",
    "prev": null,
    "next": null
  },
  "meta": {
    "current_page": 1,
    "from": 1,
    "last_page": 1,
    "path": "https:\/\/app.monicahq.com\/api\/contacts\/1\/reminders",
    "per_page": 10,
    "to": 1,
    "total": 1
  }
}
```

### Get a specific reminder

**GET** `/reminders/:id`

#### Response

```json
{
  "data": {
    "id": 2,
    "object": "reminder",
    "title": "Wish happy birthday to Jean",
    "description": null,
    "frequency_type": "year",
    "frequency_number": 1,
    "last_triggered_date": null,
    "next_expected_date": "2017-10-23T00:00:18Z",
    "account": {
      "id": 1
    },
    "contact": {
      "id": 1,
      "object": "contact",
      "first_name": "Jean",
      "last_name": "Valjean",
      "gender": "female",
      "is_partial": false,
      "information": {
        "dates": [
          {
            "name": "birthdate",
            "is_birthdate_approximate": "exact",
            "birthdate": "1983-10-23T19:10:42Z"
          }
        ]
      },
      "account": {
        "id": 1
      }
    },
    "created_at": "2016-10-07T11:53:43Z",
    "updated_at": "2017-06-16T19:04:54Z"
  }
}
```

### Create a reminder

**POST** `/reminder/`

#### Input

| Name | Type | Description |
| --- | --- | --- |
| title | string | **Required**. The title of the reminder. Max 100000 characters. |
| description | string | A description about what the reminder is. Max 1000000 characters. |
| next_expected_date | string | **Required**. The date, in the future, when we should warn the user about this reminder. Format: YYYY-MM-DD. |
| frequency_type | string | **Required**. The frequency type indicates if the reminder is recurring and if so, what it is. Possible values: `one_time`, `week`, `month`, `year`. |
| frequency_number | integer | The frequency of which the event should occur. |
| contact_id | integer | **Required**. The ID of the contact that the call is associated with. |

#### Example

```json
{
  "title": "Call to make sure everything's fine",
  "description": "I want to make sure that everything is ok about him and his wedding.",
  "next_expected_date": "2018-09-09",
  "frequency_type": "day",
  "frequency_number": 3,
  "contact_id": 1
}
```

#### Response

The API call returns a Reminder object if the call succeeds.

```json
{
  "data": {
    "id": 2,
    "object": "reminder",
    "title": "Call to make sure everything's fine",
    "description": "I want to make sure that everything is ok about him and his wedding.",
    "frequency_type": "day",
    "frequency_number": 3,
    "last_triggered_date": null,
    "next_expected_date": "2018-09-09T00:00:18Z",
    "account": {
      "id": 1
    },
    "contact": {
      "id": 1,
      "object": "contact",
      "first_name": "Jean",
      "last_name": "Valjean",
      "gender": "female",
      "is_partial": false,
      "information": {
        "dates": [
          {
            "name": "birthdate",
            "is_birthdate_approximate": "exact",
            "birthdate": "1983-10-23T19:10:42Z"
          }
        ]
      },
      "account": {
        "id": 1
      }
    },
    "created_at": "2016-10-07T11:53:43Z",
    "updated_at": "2017-06-16T19:04:54Z"
  }
}
```

### Update a reminder

**PUT** `/reminders/:id`

#### Input

| Name | Type | Description |
| --- | --- | --- |
| title | string | **Required**. The title of the reminder. Max 100000 characters. |
| description | string | A description about what the reminder is. Max 1000000 characters. |
| next_expected_date | string | **Required**. The date, in the future, when we should warn the user about this reminder. Format: YYYY-MM-DD. |
| frequency_type | string | **Required**. The frequency type indicates if the reminder is recurring and if so, what it is. Possible values: `one_time`, `week`, `month`, `year`. |
| frequency_number | integer | The frequency of which the event should occur. |
| contact_id | integer | **Required**. The ID of the contact that the call is associated with. |

#### Example

```json
{
  "title": "Call to make sure everything's fine",
  "description": "I want to make sure that everything is ok about him and his wedding.",
  "next_expected_date": "2018-09-09",
  "frequency_type": "day",
  "frequency_number": 3,
  "contact_id": 3
}
```

#### Response

```json
{
  "data": {
    "id": 2,
    "object": "reminder",
    "title": "Call to make sure everything's fine",
    "description": "I want to make sure that everything is ok about him and his wedding.",
    "frequency_type": "day",
    "frequency_number": 3,
    "last_triggered_date": null,
    "next_expected_date": "2018-09-09T00:00:18Z",
    "account": {
      "id": 1
    },
    "contact": {
      "id": 1,
      "object": "contact",
      "first_name": "Jean",
      "last_name": "Valjean",
      "gender": "female",
      "is_partial": false,
      "information": {
        "dates": [
          {
            "name": "birthdate",
            "is_birthdate_approximate": "exact",
            "birthdate": "1983-10-23T19:10:42Z"
          }
        ]
      },
      "account": {
        "id": 1
      }
    },
    "created_at": "2016-10-07T11:53:43Z",
    "updated_at": "2017-06-16T19:04:54Z"
  }
}
```

### Delete a reminder

**DELETE** `/reminders/:id`

#### Response

The response sends back the id that was just deleted.

```json
{
  "deleted": true,
  "id": 31
}
```

---

## Tasks

### Overview

The Task object allows to add tasks about your contacts.

When retrieving a task, we always also return some basic information about the related contact.

### List all the tasks in your account

**GET** `/tasks/`

#### Parameters

| Name | Type | Description |
| --- | --- | --- |
| limit | integer | Indicates the page size. |
| page | integer | Indicates the page to return. |

#### Response

```json
{
  "data": [
    {
      "id": 809,
      "object": "task",
      "title": "Send Phillys all my love",
      "description": "",
      "completed": false,
      "completed_at": null,
      "account": {
        "id": 1
      },
      "contact": {
        "id": 1,
        "object": "contact",
        "first_name": "Jim",
        "last_name": "Helpert",
        "gender": "female",
        "is_partial": false,
        "information": {
          "dates": [
            {
              "name": "birthdate",
              "is_birthdate_approximate": "exact",
              "birthdate": "1983-10-23T19:10:42Z"
            }
          ]
        },
        "account": {
          "id": 1
        }
      },
      "created_at": "2017-10-13T21:58:40Z",
      "updated_at": "2017-10-13T21:58:40Z"
    }
  ],
  "links": {
    "first": "https:\/\/app.monicahq.com\/api\/tasks?page=1",
    "last": "https:\/\/app.monicahq.com\/api\/tasks?page=1",
    "prev": null,
    "next": null
  },
  "meta": {
    "current_page": 1,
    "from": 1,
    "last_page": 1,
    "path": "https:\/\/app.monicahq.com\/api\/tasks",
    "per_page": 10,
    "to": 2,
    "total": 2
  }
}
```

#### Sorting

You can sort this query. Accepted criteria are:

| Name | Description |
| --- | --- |
| `created_at` | Will add `order by created_at asc` to the query |
| `-created_at` | Will add `order by created_at desc` to the query |
| `updated_at` | Will add `order by updated_at asc` to the query |
| `-updated_at` | Will add `order by updated_at desc` to the query |
| `completed_at` | Will add `order by completed_at asc` to the query |
| `-completed_at` | Will add `order by completed_at desc` to the query |

### List all the tasks of a specific contact

**GET** `/contacts/:id/tasks`

#### Response

```json
{
  "data": [
    {
      "id": 809,
      "object": "task",
      "title": "Send Phillys all my love",
      "description": "",
      "completed": false,
      "completed_at": null,
      "account": {
        "id": 1
      },
      "contact": {
        "id": 1,
        "object": "contact",
        "first_name": "Jim",
        "last_name": "Helpert",
        "gender": "female",
        "is_partial": false,
        "information": {
          "dates": [
            {
              "name": "birthdate",
              "is_birthdate_approximate": "exact",
              "birthdate": "1983-10-23T19:10:42Z"
            }
          ]
        },
        "account": {
          "id": 1
        }
      },
      "created_at": "2017-10-13T21:58:40Z",
      "updated_at": "2017-10-13T21:58:40Z"
    }
  ],
  "links": {
    "first": "https:\/\/app.monicahq.com\/api\/tasks?page=1",
    "last": "https:\/\/app.monicahq.com\/api\/tasks?page=1",
    "prev": null,
    "next": null
  },
  "meta": {
    "current_page": 1,
    "from": 1,
    "last_page": 1,
    "path": "https:\/\/app.monicahq.com\/api\/tasks",
    "per_page": 10,
    "to": 2,
    "total": 2
  }
}
```

### Get a specific task

**GET** `/tasks/:id`

#### Response

```json
{
  "data": {
    "id": 809,
    "object": "task",
    "title": "Send Phillys all my love",
    "description": "",
    "completed": false,
    "completed_at": null,
    "account": {
      "id": 1
    },
    "contact": {
      "id": 1,
      "object": "contact",
      "first_name": "Dwight",
      "last_name": "Schrutt",
      "gender": "male",
      "is_partial": false,
      "information": {
        "dates": [
          {
            "name": "birthdate",
            "is_birthdate_approximate": "exact",
            "birthdate": "1983-10-23T19:10:42Z"
          }
        ]
      },
      "account": {
        "id": 1
      }
    },
    "created_at": "2017-10-13T21:58:40Z",
    "updated_at": "2017-10-13T21:58:40Z"
  }
}
```

### Create a task

**POST** `/task/`

#### Input

| Name | Type | Description |
| --- | --- | --- |
| title | string | **Required**. The title of the task. Max 255 characters. |
| description | string | A description about what the task is. Max 1000000 characters. |
| completed | integer | **Required**. The status of the task. Values: `0` (false), `1` (true). |
| completed_at | string | The date the task happened. Can be in the past or future - the latter being dumb, but well. Format: YYYY-MM-DD. |
| contact_id | integer | **Required**. The ID of the contact that the call is associated with. |

#### Example

```json
{
  "title": "Bring back the table",
  "description": "I borrowed a table a while ago.",
  "completed": 0,
  "contact_id": 1
}
```

#### Response

The API call returns a task object if the call succeeds.

```json
{
  "data": {
    "id": 811,
    "object": "task",
    "title": "Bring back the table",
    "description": "I borrowed a table a while ago.",
    "completed": false,
    "completed_at": null,
    "account": {
      "id": 1
    },
    "contact": {
      "id": 1,
      "object": "contact",
      "first_name": "Michael",
      "last_name": "Scott",
      "gender": "female",
      "is_partial": false,
      "information": {
        "dates": [
          {
            "name": "birthdate",
            "is_birthdate_approximate": "exact",
            "birthdate": "1983-10-23T19:10:42Z"
          }
        ]
      },
      "account": {
        "id": 1
      }
    },
    "created_at": "2017-10-13T22:12:05Z",
    "updated_at": "2017-10-13T22:12:05Z"
  }
}
```

### Update a task

**PUT** `/tasks/:id`

#### Input

| Name | Type | Description |
| --- | --- | --- |
| title | string | **Required**. The title of the task. Max 255 characters. |
| description | string | A description about what the task is. Max 1000000 characters. |
| completed | integer | **Required**. The status of the task. Values: `0` (false), `1` (true). |
| completed_at | string | The date the task happened. Can be in the past or future - the latter being dumb, but well. Format: YYYY-MM-DD. |
| contact_id | integer | **Required**. The ID of the contact that the call is associated with. |

#### Example

```json
{
  "title": "Bring back the table",
  "description": "I borrowed a table a while ago.",
  "completed": 1,
  "completed_at": "1970-03-03",
  "contact_id": 1
}
```

#### Response

```json
{
  "data": {
    "id": 811,
    "object": "task",
    "title": "Bring back the table",
    "description": "I borrowed a table a while ago.",
    "completed": true,
    "completed_at": "1970-03-03T00:00:00Z",
    "account": {
      "id": 1
    },
    "contact": {
      "id": 1,
      "object": "contact",
      "first_name": "Michael",
      "last_name": "Scott",
      "gender": "female",
      "is_partial": false,
      "information": {
        "dates": [
          {
            "name": "birthdate",
            "is_birthdate_approximate": "exact",
            "birthdate": "1983-10-23T19:10:42Z"
          }
        ]
      },
      "account": {
        "id": 1
      }
    },
    "created_at": "2017-10-13T22:12:05Z",
    "updated_at": "2017-10-13T22:14:33Z"
  }
}
```

### Delete a task

**DELETE** `/tasks/:id`

#### Response

The response sends back the id that was just deleted.

```json
{
  "deleted": true,
  "id": 31
}
```

---

## Tags

### Overview

The Tag object allows to tag contacts. Think of tags as labels, or folders, with which you can group contacts who belong together.

### List all your tags

**GET** `/tags/`

#### Parameters

| Name | Type | Description |
| --- | --- | --- |
| limit | integer | Indicates the page size. |
| page | integer | Indicates the page to return. |

#### Response

```json
{
  "data": [
    {
      "id": 325,
      "object": "tag",
      "name": "ami",
      "name_slug": "ami",
      "account": {
        "id": 1
      },
      "created_at": "2017-07-19T21:00:07Z",
      "updated_at": "2017-07-19T21:00:07Z"
    },
    {
      "id": 857,
      "object": "tag",
      "name": "college",
      "name_slug": "college",
      "account": {
        "id": 1
      },
      "created_at": "2017-09-26T20:51:59Z",
      "updated_at": "2017-09-26T20:51:59Z"
    }
  ],
  "links": {
    "first": "https://app.monicahq.com/api/tags?page=1",
    "last": "https://app.monicahq.com/api/tags?page=1",
    "prev": null,
    "next": null
  },
  "meta": {
    "current_page": 1,
    "from": 1,
    "last_page": 1,
    "path": "https://app.monicahq.com/api/tags",
    "per_page": 10,
    "to": 5,
    "total": 5
  }
}
```

### Get a specific tag

**GET** `/tags/:id`

```json
{
  "data": {
    "id": 1,
    "object": "tag",
    "name": "collegue",
    "name_slug": "collegue",
    "account": {
      "id": 1
    },
    "created_at": "2017-07-04T22:15:03Z",
    "updated_at": "2017-07-04T22:15:03Z"
  }
}
```

### Create a tag

**POST** `/tags/`

#### Input

If a field is not required, you can send the `null` value as the content of the field.

| Name | Type | Description |
| --- | --- | --- |
| name | string | **Required**. The name of the tag. Max 255 characters. |

#### Example

```json
{
  "name": "friends"
}
```

#### Response

The API call returns a tag object if the call succeeds.

```json
{
  "data": {
    "id": 1,
    "object": "tag",
    "name": "friends",
    "name_slug": "friends",
    "account": {
      "id": 1
    },
    "created_at": "2017-07-04T22:15:03Z",
    "updated_at": "2017-07-04T22:15:03Z"
  }
}
```

### Update a tag

**PUT** `/tags/:id`

#### Input

| Name | Type | Description |
| --- | --- | --- |
| name | string | **Required**. The name of the tag. Max 255 characters. |

#### Example

```json
{
  "name": "prison"
}
```

#### Response

```json
{
  "data": {
    "id": 1,
    "object": "tag",
    "name": "prison",
    "name_slug": "prison",
    "account": {
      "id": 1
    },
    "created_at": "2017-07-04T22:15:03Z",
    "updated_at": "2017-07-04T22:15:03Z"
  }
}
```

### Delete a tag

**DELETE** `/tags/:id`

#### Response

The response sends back the id that was just deleted.

```json
{
  "deleted": true,
  "id": 31
}
```

### Associate a tag to a contact

A tag is only useful if linked to a contact. To associate a tag to a contact, simply call the following method and give an array of tag name. The call automatically manages whether a tag with the given name already exists and will only create tags that do not exist yet.

Let's say that you have one tag in your account, called `family`. Let's also assume that you are sending this array:

```json
{
  "tags": ["family", "friend"]
}
```

`friend` does not exist yet in the user's account, therefore it will be automatically created, whereas the `family` tag will not be created and only be associated with the contact.

Please note that calling this method will add the given tags to the contact without removing those which might already be associated with the contact.

**POST** `/contacts/:id/setTags`

#### Parameters

| Name | Type | Description |
| --- | --- | --- |
| tags | array | **Required**. A list of tags, as string, separated by a comma. |

#### Example

```json
{
  "tags": ["family", "friend"]
}
```

#### Response

The response sends back a standard Contact object.

### Remove a specific tag from a contact

The call lets you remove one or multiple tags from a contact. The difference with the tag creation method is the fact that this call accepts a list of ids of the tags, not a list of tag names. This is because when you create a tag, you don't want to deal with creating a tag first, then take the id and pass it to the creation method call. However, when you remove a tag, you know the id of the tag you want to remove.

The call does not delete the actual tag. It only removes the association.

**POST** `/contacts/:id/unsetTag`

#### Parameters

| Name | Type | Description |
| --- | --- | --- |
| tags | array | **Required**. A list of tag ids, as integer, separated by a comma. |

#### Example

```json
{
  "tags": [1]
}
```

#### Response

The response sends back a standard Contact object.

### Remove all the tags from a contact

If you need to remove all the tags associated with a contact, you can use this method. Note that the call does not delete the tags, it only removes the association.

**POST** `/contacts/:id/unsetTags`

#### Response

The response sends back a standard Contact object.

---

*Documentation last updated: February 2025*
*Source: https://www.monicahq.com/api*
