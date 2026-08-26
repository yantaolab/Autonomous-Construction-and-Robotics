const profilePath = "data/profile.json";

function addTags(elementId, items) {
  document.getElementById(elementId).innerHTML = items.map((item) => `<span>${item}</span>`).join("");
}

function renderProfile(profile) {
  document.title = `${profile.name} | Academic Homepage`;
  document.getElementById("name").textContent = profile.name;
  document.getElementById("headline").textContent = `${profile.major} · ${profile.year} · ${profile.university}`;
  document.getElementById("bio").textContent = profile.bio;
  document.getElementById("education").textContent = profile.education;
  document.getElementById("email").innerHTML = `<a href="mailto:${profile.email}">${profile.email}</a>`;
  addTags("interests", profile.interests);
  addTags("skills", profile.skills);
  document.getElementById("projects").innerHTML = profile.projects.map((project) => `
    <article class="project"><h3>${project.title}</h3><p>${project.description}</p></article>`).join("");
}

fetch(profilePath).then((response) => {
  if (!response.ok) throw new Error("Could not read profile data");
  return response.json();
}).then(renderProfile).catch((error) => {
  document.getElementById("name").textContent = "Profile data could not be loaded";
  document.getElementById("bio").textContent = "Start a local web server, then edit data/profile.json with your own information.";
  console.error(error);
});
