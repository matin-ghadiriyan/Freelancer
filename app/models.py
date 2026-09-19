"""Database models for the freelancer platform."""

from __future__ import annotations

from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


# --------------------------------------------------------------------------- #
#  Association tables
# --------------------------------------------------------------------------- #

project_skills = db.Table(
    "project_skills",
    db.Column("project_id", db.Integer, db.ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
    db.Column("skill_id", db.Integer, db.ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
)

freelancer_skills = db.Table(
    "freelancer_skills",
    db.Column("freelancer_id", db.Integer, db.ForeignKey("freelancer_profiles.id", ondelete="CASCADE"), primary_key=True),
    db.Column("skill_id", db.Integer, db.ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
)


# --------------------------------------------------------------------------- #
#  Users
# --------------------------------------------------------------------------- #

class User(db.Model):
    """A platform account. Can act as a client, a freelancer, or both."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar_url = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    country = db.Column(db.String(80), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # relationships
    freelancer_profile = db.relationship(
        "FreelancerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    posted_projects = db.relationship(
        "Project", back_populates="client", foreign_keys="Project.client_id", cascade="all, delete-orphan"
    )
    proposals = db.relationship(
        "Proposal", back_populates="freelancer", foreign_keys="Proposal.freelancer_id", cascade="all, delete-orphan"
    )
    reviews_written = db.relationship(
        "Review", back_populates="author", foreign_keys="Review.author_id", cascade="all, delete-orphan"
    )
    reviews_received = db.relationship(
        "Review", back_populates="target", foreign_keys="Review.target_id", cascade="all, delete-orphan"
    )

    # --- helpers ---------------------------------------------------------- #
    def set_password(self, raw: str) -> None:
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw: str) -> bool:
        return check_password_hash(self.password_hash, raw)

    @property
    def average_rating(self) -> float:
        if not self.reviews_received:
            return 0.0
        return round(sum(r.rating for r in self.reviews_received) / len(self.reviews_received), 2)

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<User {self.email}>"


# --------------------------------------------------------------------------- #
#  Freelancer profile
# --------------------------------------------------------------------------- #

class FreelancerProfile(db.Model):
    """Extra data for users that offer services."""

    __tablename__ = "freelancer_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    headline = db.Column(db.String(180), nullable=False)
    hourly_rate = db.Column(db.Numeric(10, 2), nullable=True)
    experience_years = db.Column(db.Integer, default=0, nullable=False)
    availability = db.Column(db.String(30), default="available", nullable=False)  # available | busy | away
    total_earned = db.Column(db.Numeric(12, 2), default=0, nullable=False)
    success_rate = db.Column(db.Integer, default=100, nullable=False)  # percentage
    portfolio_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # relationships
    user = db.relationship("User", back_populates="freelancer_profile")
    skills = db.relationship("Skill", secondary=freelancer_skills, back_populates="freelancers")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<FreelancerProfile {self.headline}>"


# --------------------------------------------------------------------------- #
#  Skills / Categories
# --------------------------------------------------------------------------- #

class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    slug = db.Column(db.String(90), unique=True, nullable=False, index=True)
    icon = db.Column(db.String(60), nullable=True)

    projects = db.relationship("Project", secondary=project_skills, back_populates="skills")
    freelancers = db.relationship("FreelancerProfile", secondary=freelancer_skills, back_populates="skills")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Skill {self.name}>"


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(110), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(60), nullable=True)

    projects = db.relationship("Project", back_populates="category")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Category {self.name}>"


# --------------------------------------------------------------------------- #
#  Projects
# --------------------------------------------------------------------------- #

class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    slug = db.Column(db.String(220), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    budget_min = db.Column(db.Numeric(12, 2), nullable=True)
    budget_max = db.Column(db.Numeric(12, 2), nullable=True)
    currency = db.Column(db.String(10), default="USD", nullable=False)
    deadline = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(30), default="open", nullable=False)  # open | in_progress | completed | cancelled
    experience_level = db.Column(db.String(30), default="intermediate", nullable=False)  # entry | intermediate | expert
    project_type = db.Column(db.String(30), default="fixed", nullable=False)  # fixed | hourly
    is_featured = db.Column(db.Boolean, default=False, nullable=False)
    views = db.Column(db.Integer, default=0, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # relationships
    client = db.relationship("User", back_populates="posted_projects", foreign_keys=[client_id])
    category = db.relationship("Category", back_populates="projects")
    skills = db.relationship("Skill", secondary=project_skills, back_populates="projects")
    proposals = db.relationship("Proposal", back_populates="project", cascade="all, delete-orphan")

    @property
    def proposal_count(self) -> int:
        return len(self.proposals)

    @property
    def budget_display(self) -> str:
        if self.budget_min and self.budget_max:
            return f"${self.budget_min:,.0f} - ${self.budget_max:,.0f}"
        if self.budget_min:
            return f"From ${self.budget_min:,.0f}"
        if self.budget_max:
            return f"Up to ${self.budget_max:,.0f}"
        return "Negotiable"

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Project {self.title}>"


# --------------------------------------------------------------------------- #
#  Proposals
# --------------------------------------------------------------------------- #

class Proposal(db.Model):
    __tablename__ = "proposals"

    id = db.Column(db.Integer, primary_key=True)
    cover_letter = db.Column(db.Text, nullable=False)
    bid_amount = db.Column(db.Numeric(12, 2), nullable=False)
    delivery_days = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(30), default="pending", nullable=False)  # pending | accepted | rejected | withdrawn
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    freelancer_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # relationships
    project = db.relationship("Project", back_populates="proposals")
    freelancer = db.relationship("User", back_populates="proposals", foreign_keys=[freelancer_id])

    __table_args__ = (
        db.UniqueConstraint("project_id", "freelancer_id", name="uq_proposal_per_freelancer"),
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Proposal {self.id} for project {self.project_id}>"


# --------------------------------------------------------------------------- #
#  Reviews
# --------------------------------------------------------------------------- #

class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)  # 1..5
    comment = db.Column(db.Text, nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # relationships
    author = db.relationship("User", back_populates="reviews_written", foreign_keys=[author_id])
    target = db.relationship("User", back_populates="reviews_received", foreign_keys=[target_id])
    project = db.relationship("Project")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Review {self.id} - {self.rating}/5>"
