# Working on PolicyGuard

`master` is the shared project. New work starts there and comes back through a pull request. Do not commit directly to `master`.

## Branches already included

These branches are in `master`. They do not need another merge.

| Branch | What it added |
| --- | --- |
| `cursor/policyguard-claims-assistant` | The application, the evaluation, and the PolicyGuard deck |
| `feat/policyguard-ui-refresh` | The front-end refresh, merged in pull request 1 |

## Making a change

1. Update `master`.

   ```powershell
   git checkout master
   git pull
   ```

2. Start a branch from it. Use `feat/` for new work and `fix/` for a correction.

   ```powershell
   git checkout -b feat/short-description
   ```

3. Commit on that branch and push it.

   ```powershell
   git push -u origin HEAD
   ```

4. Open a pull request into `master`. Merge the pull request. That is how the change becomes part of the shared project.

Two people can work at the same time because each person has their own branch. If both edit the same file, update the branch from `master` and resolve the conflict there before merging.

## Leave these out of commits

The virtual environment, the Chroma index, `artifacts/embeddings.npy`, slide-preview images, and PowerPoint lock files (`~$*`).
