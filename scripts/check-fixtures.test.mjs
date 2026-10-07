import assert from "node:assert/strict";
import test from "node:test";
import { checkFixtures } from "./check-fixtures.mjs";

test("fixture policy defines allowed and prohibited test data", async () => {
  const errors = await checkFixtures();
  assert.deepEqual(errors, []);
});
